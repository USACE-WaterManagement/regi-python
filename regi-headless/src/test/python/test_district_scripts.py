import importlib.util
import io
import logging
import re
import sys
import types
from contextlib import redirect_stdout
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = MODULE_ROOT.parent
DISTRICT_SCRIPTS_ROOT = REPOSITORY_ROOT / "district-scripts"
EXAMPLE_SCRIPTS_ROOT = MODULE_ROOT / "src" / "test" / "resources" / "usace" / "rowcps" / "headless" / "examples"
JAVA_SOURCE_ROOT = MODULE_ROOT / "src" / "main" / "java"


JAVA_METHOD_PATTERN = re.compile(
    r"\bpublic\s+(?:static\s+)?(?:[\w<>\[\], ?]+\s+)+(?P<name>[A-Za-z_]\w*)\s*\("
)
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
    return {
        "Inflow": _java_methods(
            "usace/rowcps/headless/calculator/inflow/ScriptableInflowImpl.java"
        ),
        "Gate Flow": _java_methods(
            "usace/rowcps/headless/calculator/flowgroup/ScriptableGateFlowImpl.java"
        ),
        "Gate Settings": _java_methods(
            "usace/rowcps/headless/calculator/gatesettings/ScriptableGateSettingsImpl.java"
        ),
        "LoggingOptions": _java_methods("usace/rowcps/headless/LoggingOptions.java"),
    }


def _java_methods(relative_path):
    source = (JAVA_SOURCE_ROOT / relative_path).read_text(encoding="utf-8")
    return {
        match.group("name")
        for match in JAVA_METHOD_PATTERN.finditer(_strip_java_comments(source))
    }


def _strip_java_comments(source):
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//.*", "", source)


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
        {name: staticmethod(_noop) for name in java_api["LoggingOptions"]},
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
    def __init__(self, display_name, method_names):
        self._display_name = display_name
        self._method_names = method_names

    def __getattr__(self, name):
        if name not in self._method_names:
            raise AttributeError(f"{self._display_name} has no Java method {name!r}")
        return _noop


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


def _noop(*args, **kwargs):
    return None
