"""
Verifies JPype's automatic conversion of a plain Python `datetime.datetime`
into a `java.time.Instant`, and locks in the exact timezone behavior documented
in docs/JYTHON_TO_JPYPE_MIGRATION.md ("Date and Time Handling").

These tests start a real JVM through jpype instead of faking `java.time`,
because the point is to verify jpype's own conversion behavior rather than
our code. They only touch `java.time.Instant`, which ships in every JDK/JRE,
so no project jars or Gradle build are required -- just a JVM that jpype can
locate. If none is available, the module is skipped rather than failed.
"""

from datetime import datetime, timezone

import pytest

jpype = pytest.importorskip("jpype")
pytest.importorskip("jpype.imports")  # registers the `from java.x import Y` import hook


def _ensure_jvm_started():
    if jpype.isJVMStarted():
        return
    try:
        jpype.startJVM(jpype.getDefaultJVMPath())
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"No usable JVM available for jpype: {exc}")


@pytest.fixture(scope="module", autouse=True)
def _jvm():
    _ensure_jvm_started()
    yield
    # Deliberately not shut down: a JVM cannot be restarted once stopped in
    # the same process, and other test modules in this pytest run may still
    # need one (real or mocked).


@pytest.fixture(scope="module")
def Instant():
    from java.time import Instant as JInstant

    return JInstant


def test_utc_aware_datetime_converts_to_the_exact_instant(Instant):
    """
    A datetime whose wall-clock fields already represent UTC crosses into an
    `Instant`-typed parameter exactly.

    `compareTo`'s formal parameter type is declared as exactly `Instant`,
    which is what makes jpype's datetime -> Instant converter fire. Methods
    declared to accept `Object` (like `equals`) do NOT trigger it.
    """
    utc_dt = datetime(2018, 8, 1, 12, 30, 0, tzinfo=timezone.utc)
    expected = Instant.parse("2018-08-01T12:30:00Z")

    assert expected.compareTo(utc_dt) == 0


def test_non_utc_aware_datetime_is_silently_misread_as_utc(Instant):
    """
    Regression guard for the one rule called out in the migration doc: jpype's
    converter does not consult `tzinfo` -- it takes whatever wall-clock fields
    the datetime has and stamps them as UTC. A Central-time datetime that is
    NOT first normalized with `.astimezone(timezone.utc)` silently produces
    the wrong instant, five hours off, with no error or warning.
    """
    from zoneinfo import ZoneInfo

    central = ZoneInfo("America/Chicago")
    midnight_central = datetime(2015, 5, 1, 0, 0, 0, tzinfo=central)  # really 05:00 UTC

    what_jpype_actually_produces = Instant.parse("2015-05-01T00:00:00Z")
    what_it_should_have_meant = Instant.parse("2015-05-01T05:00:00Z")

    assert what_jpype_actually_produces.compareTo(midnight_central) == 0
    assert what_it_should_have_meant.compareTo(midnight_central) != 0


def test_astimezone_utc_before_passing_is_the_correct_pattern(Instant):
    """The documented fix: always call `.astimezone(timezone.utc)` first."""
    from zoneinfo import ZoneInfo

    central = ZoneInfo("America/Chicago")
    midnight_central = datetime(2015, 5, 1, 0, 0, 0, tzinfo=central)
    normalized = midnight_central.astimezone(timezone.utc)

    correct_instant = Instant.parse("2015-05-01T05:00:00Z")
    assert correct_instant.compareTo(normalized) == 0
