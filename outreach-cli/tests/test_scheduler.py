"""Scheduler XML-Builder Unit-Tests — kein Task wird wirklich erstellt."""

from __future__ import annotations

from datetime import datetime

import pytest

from outreach_cli.commands.scheduler import (
    TASK_NAME_PREFIX,
    WEEKLY_TASK_NAME,
    _build_one_shot_xml,
    _build_weekly_xml,
)


def test_one_shot_xml_contains_correct_trigger_and_action():
    trigger = datetime(2026, 5, 13, 14, 30, 0)
    xml = _build_one_shot_xml(
        task_name="MaxContentSEO_BounceCheck_TEST",
        trigger_at=trigger,
        cmd_args="-m outreach_cli bounce-check --tab Frankfurt_Umland",
    )
    # Trigger-Format YYYY-MM-DDTHH:MM:SS
    assert "<StartBoundary>2026-05-13T14:30:00</StartBoundary>" in xml
    # EndBoundary erforderlich für DeleteExpiredTaskAfter (sonst schtasks-Error)
    assert "<EndBoundary>2026-05-14T02:30:00</EndBoundary>" in xml  # +12h default
    # ONCE-Trigger
    assert "<TimeTrigger>" in xml
    # Action argstring
    assert "-m outreach_cli bounce-check --tab Frankfurt_Umland" in xml
    # Python launcher
    assert "<Command>py</Command>" in xml
    # XML well-formed (no unescaped ampersands)
    assert "&amp;" not in xml or xml.count("&") == xml.count("&amp;") + xml.count("&lt;") + xml.count("&gt;") + xml.count("&quot;")


def test_one_shot_xml_end_window_configurable():
    trigger = datetime(2026, 5, 13, 14, 0, 0)
    xml = _build_one_shot_xml(
        task_name="x", trigger_at=trigger, cmd_args="-m x",
        end_window_hours=24,
    )
    assert "<EndBoundary>2026-05-14T14:00:00</EndBoundary>" in xml  # +24h


def test_weekly_xml_uses_monday_default():
    xml = _build_weekly_xml(
        task_name=WEEKLY_TASK_NAME,
        cmd_args="-m outreach_cli bounce-check --all-tabs",
    )
    assert "<CalendarTrigger>" in xml
    assert "<Monday/>" in xml
    assert "-m outreach_cli bounce-check --all-tabs" in xml
    assert "<WeeksInterval>1</WeeksInterval>" in xml


def test_weekly_xml_custom_weekday_and_time():
    xml = _build_weekly_xml(
        task_name="custom",
        cmd_args="-m outreach_cli bounce-check --all-tabs",
        weekday="Friday", hour=15, minute=30,
    )
    assert "<Friday/>" in xml
    # StartBoundary contains today @ 15:30:00
    assert "T15:30:00</StartBoundary>" in xml


def test_xml_escapes_special_chars_in_cmd_args():
    xml = _build_one_shot_xml(
        task_name="x", trigger_at=datetime(2026, 5, 13, 0, 0, 0),
        cmd_args='-m outreach_cli bounce-check --tab "Bad Homburg" & echo X',
    )
    assert "&amp;" in xml
    assert "&quot;" in xml
    assert "& echo" not in xml  # raw & must not appear unescaped


def test_task_name_prefix_constant():
    """Stabilität — bricht den Auto-Schedule wenn umbenannt."""
    assert TASK_NAME_PREFIX == "MaxContentSEO_BounceCheck_"
    assert WEEKLY_TASK_NAME == "MaxContentSEO_WeeklyBounceCheck"
