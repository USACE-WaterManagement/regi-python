import importlib.util
import io
import logging
import os
import re
import sys
import types
from contextlib import redirect_stdout
from pathlib import Path

import jpype
import pytest


MODULE_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = MODULE_ROOT.parent

# Gradle knows these paths authoritatively (see the `smokeTestDistrictScripts`
# task in build.gradle) and passes them in as environment variables. The
# fallback here -- walking up from this file's own location -- only exists
# so the test still works when run directly without going through Gradle.
DISTRICT_SCRIPTS_ROOT = Path(
    os.environ.get("DISTRICT_SCRIPTS_DIR", str(REPOSITORY_ROOT / "district-scripts"))
)
EXAMPLE_SCRIPTS_ROOT = Path(
    os.environ.get(
        "EXAMPLE_SCRIPTS_DIR",
        str(MODULE_ROOT / "src" / "test" / "resources" / "usace" / "rowcps" / "headless" / "examples"),
    )
)

# Fully-qualified Java type names this test reflects over (via the real JVM
# -- see conftest.py for the classpath setup) to build the "known scriptable
# API" that district/example scripts are allowed to call.
#
# These target the *interfaces* (ScriptableInflow, ScriptableGateFlowCalc,
# ScriptableGateSettings). LoggingOptions has no separate interface --
# it's a plain static utility class -- so it's targeted directly.
SCRIPTABLE_JAVA_CLASSES = {
    "Inflow": "usace.rowcps.headless.calculator.inflow.ScriptableInflow",
    "Gate Flow": "usace.rowcps.headless.calculator.flowgroup.ScriptableGateFlowCalc",
    "Gate Settings": "usace.rowcps.headless.calculator.gatesettings.ScriptableGateSettings",
    "LoggingOptions": "usace.rowcps.headless.LoggingOptions",
}

LOGGER = logging.getLogger(__name__)


def test_migrated_scripts_only_call_known_scriptable_api(monkeypatch):
    java_api = _load_java_api()
    _install_fake_modules(monkeypatch, java_api)

    _validate_scripts("district", DISTRICT_SCRIPTS_ROOT, _district_scripts(), java_api)
    _validate_scripts("example", EXAMPLE_SCRIPTS_ROOT, _example_scripts(), java_api)


def _validate_scripts(label, root, scripts, java_api):
    assert scripts, f"No {label} scripts found under {root}"
    LOGGER.info("Validating %s %s script(s)", len(scripts), label)

    failures = []
    for script in scripts:
        relative_script = script.relative_to(REPOSITORY_ROOT)
        LOGGER.info("Validating %s script: %s", label, relative_script)
        try:
            module = _load_script(script)
            with redirect_stdout(io.StringIO()):
                _script_callback(module)(FakeRegistry(java_api))
        except Exception as exc:
            failures.append(f"{relative_script}: {type(exc).__name__}: {exc}")
        else:
            LOGGER.info("Validated %s script: %s", label, relative_script)

    assert not failures, f"{label.title()} script API validation failed:\n" + "\n".join(failures)


def _district_scripts():
    return sorted(
        path
        for path in DISTRICT_SCRIPTS_ROOT.rglob("*.py")
        if path.name != "__init__.py"
    )


def _example_scripts():
    return sorted(
        path
        for path in EXAMPLE_SCRIPTS_ROOT.rglob("*.py")
        if path.name != "__init__.py"
    )


def _script_callback(module):
    for name in (
        "run_calculations",
        "calculate_inflow",
        "calculate_gate_flow",
        "calculate_gate_settings",
        "configure_logging_options",
    ):
        callback = getattr(module, name, None)
        if callback is not None:
            return callback
    raise AssertionError(f"No migrated script callback found in {module.__file__}")


def _load_java_api():
    """
    Reflects over the actual compiled classes via JPype/JVM reflection to
    build: display name -> {method name -> [overload parameter-type tuples]}.
    """
    java_lang_class = jpype.JClass("java.lang.Class")
    modifier = jpype.JClass("java.lang.reflect.Modifier")

    try:
        return {
            display_name: _java_method_signatures(java_lang_class, modifier, fqcn)
            for display_name, fqcn in SCRIPTABLE_JAVA_CLASSES.items()
        }
    except jpype.JException as exc:
        pytest.skip(
            "Could not load the REGI Headless classes for reflection. Run the "
            "Gradle 'bundlePython' (or 'installPythonWheelForSmokeTest') task "
            f"to build/install the jars first: {exc}"
        )


def _java_method_signatures(java_lang_class, modifier, fully_qualified_name):
    java_class = java_lang_class.forName(fully_qualified_name)
    signatures = {}
    for method in java_class.getDeclaredMethods():
        if not modifier.isPublic(method.getModifiers()):
            continue
        name = str(method.getName())
        parameter_types = tuple(
            str(parameter_type.getName()) for parameter_type in method.getParameterTypes()
        )
        signatures.setdefault(name, []).append(parameter_types)
    return signatures


def _load_script(path):
    module_name = "district_script_" + re.sub(r"\W+", "_", str(path.relative_to(REPOSITORY_ROOT)))
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _install_fake_modules(monkeypatch, java_api):
    modules = {}

    def module(name):
        value = modules.get(name)
        if value is None:
            value = types.ModuleType(name)
            modules[name] = value
            monkeypatch.setitem(sys.modules, name, value)
            if "." in name:
                parent_name, child_name = name.rsplit(".", 1)
                setattr(module(parent_name), child_name, value)
        return value

    regi_python = module("regi_python")
    regi_python.regi_session = _fake_regi_session
    regi_python.run_headless = lambda callback: callback(FakeRegistry(java_api))

    java_util = module("java.util")
    java_util.Calendar = FakeCalendar
    java_util.TimeZone = FakeTimeZone

    java_lang = module("java.lang")
    java_lang.System = FakeSystem

    headless = module("usace.rowcps.headless")
    headless.LoggingOptions = type(
        "LoggingOptions",
        (),
        {
            name: staticmethod(_make_validated_stub("LoggingOptions", name, overloads))
            for name, overloads in java_api["LoggingOptions"].items()
        },
    )

    inflow = module("usace.rowcps.headless.calculator.inflow")
    inflow.InflowComputationStorageOption = types.SimpleNamespace(
        EVAP_AS_FLOW="EVAP_AS_FLOW",
        PROJECT_RELEASES="PROJECT_RELEASES",
    )


class _fake_regi_session:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, traceback):
        return False


# Best-effort category buckets used to flag obviously-wrong argument types
# (e.g. a string passed where every known overload expects a number) without
# trying to fully replicate the JVM's overload resolution -- JPype's own
# implicit Python -> Java conversions make mirroring that exactly impractical.
_NUMERIC_JAVA_TYPES = {
    "int", "long", "short", "byte", "float", "double",
    "java.lang.Integer", "java.lang.Long", "java.lang.Short", "java.lang.Byte",
    "java.lang.Float", "java.lang.Double", "java.math.BigDecimal", "java.math.BigInteger",
}
_BOOLEAN_JAVA_TYPES = {"boolean", "java.lang.Boolean"}
_STRING_JAVA_TYPES = {"java.lang.String", "java.lang.CharSequence"}
_KNOWN_CATEGORIES = {"numeric", "boolean", "string"}


def _java_type_category(type_name):
    if type_name in _NUMERIC_JAVA_TYPES:
        return "numeric"
    if type_name in _BOOLEAN_JAVA_TYPES:
        return "boolean"
    if type_name in _STRING_JAVA_TYPES:
        return "string"
    return "other"


def _python_type_category(value):
    if isinstance(value, bool):  # must precede int check: bool is an int subclass
        return "boolean"
    if isinstance(value, (int, float)):
        return "numeric"
    if isinstance(value, str):
        return "string"
    return "other"


def _overload_accepts(parameter_types, args):
    for type_name, arg in zip(parameter_types, args):
        java_category = _java_type_category(type_name)
        python_category = _python_type_category(arg)
        if (
            java_category in _KNOWN_CATEGORIES
            and python_category in _KNOWN_CATEGORIES
            and java_category != python_category
        ):
            return False
    return True


def _make_validated_stub(display_name, method_name, overloads):
    """
    Builds a fake implementation of a Java method that validates positional
    call arguments against the method's real, reflected overload(s): arity
    always, and argument type "category" (numeric/boolean/string) wherever
    that's unambiguous.
    """
    arities = sorted({len(parameter_types) for parameter_types in overloads})

    def stub(*args, **kwargs):
        same_arity_overloads = [p for p in overloads if len(p) == len(args)]
        if not same_arity_overloads:
            raise TypeError(
                f"{display_name}.{method_name}() called with {len(args)} positional "
                f"argument(s); known overload(s) take {arities} argument(s)"
            )
        if any(_overload_accepts(p, args) for p in same_arity_overloads):
            return None
        expected = " or ".join(f"({', '.join(p)})" for p in same_arity_overloads)
        got = ", ".join(type(arg).__name__ for arg in args)
        raise TypeError(
            f"{display_name}.{method_name}() called with argument types ({got}), "
            f"which does not match any known overload: {expected}"
        )

    return stub


class FakeRegistry:
    def __init__(self, java_api):
        self._java_api = java_api

    def getNames(self, version):
        return ["Inflow", "Gate Flow", "Gate Settings"]

    def getCalculation(self, version, name):
        if name not in self._java_api:
            raise AssertionError(f"Unknown calculation requested: {name!r}")
        return FakeJavaObject(name, self._java_api[name])


class FakeJavaObject:
    def __init__(self, display_name, method_signatures):
        self._display_name = display_name
        self._method_signatures = method_signatures

    def __getattr__(self, name):
        overloads = self._method_signatures.get(name)
        if overloads is None:
            raise AttributeError(f"{self._display_name} has no Java method {name!r}")
        return _make_validated_stub(self._display_name, name, overloads)


class FakeTimeZone:
    @staticmethod
    def getTimeZone(name):
        return FakeTimeZone()


class FakeSystem:
    @staticmethod
    def getProperty(name):
        return ""


class FakeCalendar:
    DATE = 1
    DAY_OF_MONTH = 2
    HOUR = 3
    HOUR_OF_DAY = 4
    MILLISECOND = 5
    MINUTE = 6
    MONTH = 7
    SECOND = 8
    YEAR = 9

    @staticmethod
    def getInstance(time_zone=None):
        return FakeCalendar()

    def add(self, field, amount):
        return None

    def clear(self):
        return None

    def getTime(self):
        return FakeDate()

    def getTimeInMillis(self):
        return 0

    def get(self, field):
        return 0

    def set(self, field, value):
        return None


class FakeDate:
    def getTime(self):
        return 0

    def toString(self):
        return "FakeDate"
