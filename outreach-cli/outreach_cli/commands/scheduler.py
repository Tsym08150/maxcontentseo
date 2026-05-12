"""Windows Task Scheduler Integration via schtasks.exe.

Wir benutzen XML-Tasks (statt der CLI-Flags), weil schtasks /Create mit /SD/ST
locale-abhängige Datumsformate braucht (DE: dd.mm.yyyy, EN: mm/dd/yyyy).
XML-Mode ist locale-agnostisch und expressiver.

Drei Funktionen:
  - schedule_one_shot_bounce_check(...) — 24h nach jetzt, ONCE-Trigger
  - schedule_weekly_bounce_check() — jeden Montag 09:00, WEEKLY-Trigger
  - delete_task(name) — idempotent (kein Fehler wenn Task nicht existiert)
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


TASK_NAME_PREFIX = "MaxContentSEO_BounceCheck_"
WEEKLY_TASK_NAME = "MaxContentSEO_WeeklyBounceCheck"


@dataclass(frozen=True)
class ScheduleResult:
    task_name: str
    trigger_at: datetime
    action_cmd: str
    schtasks_output: str
    ok: bool


def _python_invocation() -> str:
    """Python-Aufruf rekonstruieren — bevorzugt `py` (Windows Python Launcher),
    Fallback: sys.executable.

    Wir verwenden `py -m outreach_cli`, weil das stabiler ist als ein vollqualifizierter
    Pfad zu einem virtualenv-Python (der Pfad könnte sich ändern).
    """
    return "py"


def _outreach_cwd() -> str:
    """Der Working-Directory, in dem `py -m outreach_cli` läuft.

    Wir nehmen das Repo-Root (zwei Ebenen über diesem Modul): scripts/commands/scheduler.py
    → ../../../ ist Repo-Root.

    HINWEIS: pyproject.toml + outreach_cli/ liegen in outreach-cli/ — das ist der working dir.
    """
    # scheduler.py liegt in outreach_cli/commands/ → parent.parent ist outreach-cli/
    return str(Path(__file__).resolve().parent.parent.parent)


def _build_one_shot_xml(
    *,
    task_name: str,
    trigger_at: datetime,
    cmd_args: str,
    description: str = "Bounce-Check 24h nach Outreach-Versand",
) -> str:
    """ONCE-Trigger XML für schtasks /XML."""
    # XML-Datetime-Format: YYYY-MM-DDTHH:MM:SS
    start = trigger_at.strftime("%Y-%m-%dT%H:%M:%S")
    cwd = _outreach_cwd()
    # XML-escape die paar Sonderzeichen die in cmd_args + cwd vorkommen könnten
    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>{esc(description)}</Description>
    <Author>outreach-cli</Author>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <StartBoundary>{start}</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
    <DeleteExpiredTaskAfter>P1D</DeleteExpiredTaskAfter>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{esc(_python_invocation())}</Command>
      <Arguments>{esc(cmd_args)}</Arguments>
      <WorkingDirectory>{esc(cwd)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""


def _build_weekly_xml(
    *,
    task_name: str,
    cmd_args: str,
    weekday: str = "Monday",
    hour: int = 9,
    minute: int = 0,
    description: str = "Wöchentlicher Bounce-Check über alle Tabs",
) -> str:
    """WEEKLY-Trigger XML — Montag 09:00 Standard."""
    cwd = _outreach_cwd()
    today = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    start = today.strftime("%Y-%m-%dT%H:%M:%S")
    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>{esc(description)}</Description>
    <Author>outreach-cli</Author>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{start}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek><{weekday}/></DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{esc(_python_invocation())}</Command>
      <Arguments>{esc(cmd_args)}</Arguments>
      <WorkingDirectory>{esc(cwd)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""


def _run_schtasks(args: list[str], xml: Optional[str] = None) -> tuple[int, str]:
    """Wrapper um schtasks.exe. XML als UTF-16-BOM-File übergeben (Win-Konvention).

    Returns (returncode, stdout+stderr).
    """
    # Wenn XML übergeben: temp-File mit UTF-16 BOM schreiben
    if xml is not None:
        # schtasks /XML braucht UTF-16 LE mit BOM
        fd, path = tempfile.mkstemp(suffix=".xml", prefix="outreach_task_")
        try:
            os.close(fd)
            Path(path).write_text(xml, encoding="utf-16")
            args_with_xml = args + ["/XML", path]
            proc = subprocess.run(
                ["schtasks.exe"] + args_with_xml,
                capture_output=True, text=True, shell=False,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            return proc.returncode, output
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
    else:
        proc = subprocess.run(
            ["schtasks.exe"] + args,
            capture_output=True, text=True, shell=False,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def delete_task(name: str) -> tuple[int, str]:
    """Idempotent: kein Fehler wenn Task nicht existiert."""
    rc, out = _run_schtasks(["/Delete", "/TN", name, "/F"])
    # rc != 0 wenn Task nicht existiert — das ist OK
    return rc, out


def schedule_one_shot_bounce_check(
    *,
    tab: str,
    trigger_at: Optional[datetime] = None,
    delay_hours: int = 24,
    task_suffix: Optional[str] = None,
) -> ScheduleResult:
    """Einmaliger Task: bounce-check auf `tab`, 24h nach jetzt (oder `trigger_at`)."""
    if trigger_at is None:
        trigger_at = datetime.now() + timedelta(hours=delay_hours)

    suffix = task_suffix or datetime.now().strftime("%Y%m%d_%H%M%S")
    task_name = f"{TASK_NAME_PREFIX}{suffix}"

    cmd_args = f"-m outreach_cli bounce-check --tab {tab}"
    xml = _build_one_shot_xml(task_name=task_name, trigger_at=trigger_at, cmd_args=cmd_args)

    # Falls Task mit gleichem Namen existiert: replace via /F
    rc, out = _run_schtasks(["/Create", "/TN", task_name, "/F"], xml=xml)
    return ScheduleResult(
        task_name=task_name,
        trigger_at=trigger_at,
        action_cmd=f"py {cmd_args}",
        schtasks_output=out.strip(),
        ok=(rc == 0),
    )


def schedule_weekly_bounce_check(
    *,
    weekday: str = "Monday",
    hour: int = 9,
    minute: int = 0,
) -> ScheduleResult:
    """Wöchentlich: bounce-check über alle Tabs."""
    cmd_args = "-m outreach_cli bounce-check --all-tabs"
    xml = _build_weekly_xml(
        task_name=WEEKLY_TASK_NAME, cmd_args=cmd_args,
        weekday=weekday, hour=hour, minute=minute,
    )
    rc, out = _run_schtasks(["/Create", "/TN", WEEKLY_TASK_NAME, "/F"], xml=xml)
    trigger = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    return ScheduleResult(
        task_name=WEEKLY_TASK_NAME,
        trigger_at=trigger,
        action_cmd=f"py {cmd_args}",
        schtasks_output=out.strip(),
        ok=(rc == 0),
    )
