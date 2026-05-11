---
phase: send-command-phase-1
reviewed: 2026-05-11T00:00:00Z
depth: deep
files_reviewed: 7
files_reviewed_list:
  - outreach_cli/commands/send.py
  - outreach_cli/templates/engine.py
  - outreach_cli/templates/variante_c.txt
  - outreach_cli/leads/loader.py
  - outreach_cli/email/builder.py
  - outreach_cli/cli.py (only send command)
  - tests/test_send.py
findings:
  critical: 2
  high: 4
  medium: 7
  low: 5
  total: 18
status: issues_found
phase2_readiness: NEEDS-REFACTOR-BEFORE-SMTP
---

# Code Review — `outreach send` Phase 1 (Dry-Run)

**Reviewed:** 2026-05-11
**Depth:** deep (cross-file trace through loader → engine → builder → cli)
**Status:** issues_found
**Phase 2 verdict:** NEEDS-REFACTOR-BEFORE-SMTP — the abstraction works for dry-run but several boundaries leak details that SMTP will have to fight. See HIGH-04 and MEDIUM-02 below.

---

## Summary

The Phase-1 pipeline is functionally sound for the happy path: leads stream from sheet → filtered → render-vars derived → template rendered → .eml file written with BOM. The HWG-filter, fail-fast template, and `{stadt}`-from-column rule all work as specified.

However:

1. **CRITICAL-01 (HWG false positives):** the substring filter triggers on `arzt` inside `Praxis` (no, but inside many German nouns/names — e.g. company `"Schwarzkopf"` → matches `arzt`? No — `arzt` is not in `Schwarzkopf`. But `"Quarzteam"`, `"Tarzt..."`, surname `"Marzt..."`, or `"Bad Schwarzbach"` could match. The single-token trigger `arzt` is a substring search across the joined firma+branche string, so any word containing the letter sequence will exclude the lead. See finding for concrete examples.) Real-world fallout: leads with surnames like `Schwarzt`/`Tarzt` (admittedly rare) or branches like `"Quarz-Therapie"` would not match, but the substring approach is brittle and not what the test suite verifies — the parametrized test only checks word-aligned cases. The HWG-filter is also case-folded against `lead.firma + " | " + branche`, but if STADT contained `"Bad Arztheim"` it would not be checked — small inconsistency but worth knowing.
2. **CRITICAL-02 (BOM in .eml):** UTF-8 BOM prefixed to MIME-headers is not RFC-5322 compliant. Outlook/Thunderbird mostly tolerate this on re-import; Gmail's "Show original" / SMTP relays may treat the BOM as part of the first header line, mangling the `From:` field. The user-spec policy ("UTF-8 with BOM") was for human-readable status reports — applying it to RFC-822 envelopes is over-eager.
3. **HIGH-04 (Phase-2 abstraction):** `run_send` returns a dataclass containing rendered `.eml` paths. There is no `Transport` abstraction. When SMTP arrives tomorrow you will need to either branch inside `run_send` (already complex) or refactor the call shape. Either is fine — but flagging now so it's not a surprise.

---

## CRITICAL

### CRITICAL-01: HWG substring filter has false-positive surface, and tests do not cover it

**File:** `outreach_cli/leads/loader.py:21-29, 61-67`
**Issue:** `is_hwg_excluded` builds `haystack = f"{firma} | {branche}".lower()` and tests for substring containment. Triggers include single tokens `"arzt"`, `"aerztin"`, `"ärztin"`. Substring matching will fire on any word containing the substring:

- `"arzt"` matches inside `"Quarzthermen"`, `"Tarztherapie"`, `"Schwarztaler"` (rare German surnames/place names)
- `"ärztin"` matches inside `"Bärztrinker"` (constructed, but the principle stands)
- `"heilpraktiker"` matches inside `"Heilpraktikerschule"` (a training institution that legally is NOT under HWG)

More importantly: **the parametrized test (`test_hwg_filter_excludes_doctors`) only contains word-aligned cases and never asserts a negative on a substring-collision case.** That means future regressions are silent.

**Recommended fix:** Switch to word-boundary regex, and add a negative test:

```python
import re
_HWG_PATTERNS = tuple(
    re.compile(rf"(?<!\w){re.escape(t)}(?!\w)", re.IGNORECASE)
    for t in HWG_TRIGGERS
)

def is_hwg_excluded(lead: LeadRow) -> tuple[bool, Optional[str]]:
    haystack = f"{lead.firma} | {lead.data.get('BRANCHE', '')}"
    for trigger, pat in zip(HWG_TRIGGERS, _HWG_PATTERNS):
        if pat.search(haystack):
            return True, trigger
    return False, None
```

And add: `("Quarztherapie Salon", "Wellness", False)` and `("Heilpraktikerschule Berlin", "Bildung", False)` to the parametrized test (decide policy first — the latter is borderline and you may *want* to exclude it).

### CRITICAL-02: UTF-8 BOM prefixed to RFC-822 envelope is not standards-compliant

**File:** `outreach_cli/email/builder.py:67-72`
**Issue:** `build_eml` returns `UTF8_BOM + msg.as_bytes()`. The BOM is placed *before* the `From:` header. RFC-5322 requires the first byte of an email message to begin a header field name (printable US-ASCII). The BOM bytes (`EF BB BF`) are not header characters.

Consequences:
- Most desktop mail clients (Outlook 2016+, Thunderbird, Apple Mail) detect and strip leading BOM on `.eml` import — works in practice.
- **SMTP submission in Phase 2:** if you pass `eml_bytes` directly to `smtplib.SMTP.sendmail(from_addr, to_addrs, eml_bytes)`, the BOM will be transmitted over the wire as part of the message body. Most MTAs will accept it, but spam filters (Postfix `header_checks`, SpamAssassin) may flag it as malformed; some receivers will display a literal `` at the very top of the message.
- **Re-importing .eml into Gmail (drag-drop into Sent):** Gmail's "Upload draft" API rejects messages where the first line does not match a valid header pattern.

The user's BOM policy comes from `feedback_encoding_hieroglyphen.md` (memory: PS5.1 `WriteAllText` + UTF-8 BOM fix in ProtonMail) — that was a *file-level* encoding hint for human-readable .ps1/.md/.txt files. **A MIME message is not a text file in the same sense.**

**Recommended fix:** Drop the BOM from `build_eml`. Keep MIME headers as the first bytes. Add a separate helper for any other text output that should be BOM-prefixed.

```python
def build_eml(...) -> bytes:
    msg = MIMEText(body, _subtype="plain", _charset="utf-8")
    ...
    return msg.as_bytes()  # NO BOM
```

Update `test_dry_run_creates_eml` and `test_eml_encoding_utf8_bom` accordingly. If the user *insists* on BOM in `.eml` files for some local-archival reason, document the SMTP-strip step (`eml_bytes.lstrip(UTF8_BOM)`) that Phase-2 must do before `sendmail`.

---

## HIGH

### HIGH-01: YAML-frontmatter parser does not handle escaped quotes or backslashes inside values

**File:** `outreach_cli/templates/engine.py:77-83`
**Issue:** The handcoded parser strips matching outer single/double quotes but does not unescape `\"` or `\\`. A template author writing:

```yaml
subject: "Frage zu \"Ihrem\" Studio in {stadt}"
```

…will get `subject_tpl == 'Frage zu \\"Ihrem\\" Studio in {stadt}'` (the literal backslashes survive, the inner quotes are not unescaped). Worse: a value like `"abc"def"` (unbalanced) yields `abc"def` silently (outer quotes stripped, inner survives) — possibly intended, possibly not.

Also: a value of just `'"'` (single double-quote, length-1 string) would be `value[0:0]` after stripping → empty string, silently. The condition `value.startswith('"') and value.endswith('"')` is true for `'"'` because the same char satisfies both.

**Recommended fix:** Either reject malformed-quoted values (`len(value) >= 2` guard) or pull in `yaml.safe_load` from PyYAML (already common dependency footprint). The handcoded parser is fine for the controlled set of templates you ship, but it should at minimum guard against length-1 quoted values:

```python
if len(value) >= 2 and (
    (value[0] == '"' and value[-1] == '"') or
    (value[0] == "'" and value[-1] == "'")
):
    value = value[1:-1]
```

### HIGH-02: `parse_template` raises on frontmatter line without `:` — but matches inside multi-line values

**File:** `outreach_cli/templates/engine.py:74-76`
**Issue:** `parse_template` iterates lines between the two `---` markers and raises `TemplateParseError` for any line without `:`. This breaks legitimate YAML use cases:

```yaml
---
subject: "Mehrzeiliger
  Wert hier"
version: "C"
---
```

The continuation line `  Wert hier"` has no colon → parse error. Single-line values work, but the moment anyone adds a wrapped subject the template breaks. Probably fine for now (your one template is simple) — but worth a comment in the docstring stating "no multi-line values supported."

**Recommended fix:** Either document the limitation in the engine module docstring or add real multi-line support. Documenting is cheaper:

```python
"""...
Beschränkung: Nur einzeilige Key:Value-Paare im Frontmatter.
Multi-Line / List / Nested-Dict-Werte werden NICHT geparst — write single-line values.
"""
```

### HIGH-03: `derive_render_vars` fails the whole batch when STADT or BRANCHE is empty, but caller treats it as a fatal `ValueError`

**File:** `outreach_cli/leads/loader.py:82-100`, called from `outreach_cli/leads/loader.py:184`
**Issue:** `load_filtered_leads` calls `derive_render_vars` inside a loop without try/except. If a single lead has empty STADT or BRANCHE, the whole `load_filtered_leads` call raises `ValueError` and `run_send` propagates it. The user loses the entire batch because one row in the sheet is incomplete.

Compare: `run_send` does catch `MissingTemplateVariableError` per-lead and continues. The same robustness should apply to `derive_render_vars` failures.

**Recommended fix:** Catch the `ValueError` in `load_filtered_leads` and skip the lead, recording it in stats:

```python
# stats: add field `skipped_no_render_vars: list[str]` (email + reason)

for l in all_leads:
    try:
        vars_ = derive_render_vars(l)
    except ValueError as e:
        stats.skipped_no_render_vars.append(f"{l.email} ({l.firma}): {e}")
        continue
    results.append(FilteredLead(lead=l, render_vars=vars_))
```

Bonus: `run_send` already tracks `skipped_render_errors` — add a sibling list for `skipped_derive_vars` and report both in JSON / tabular output.

### HIGH-04: `run_send` is not abstracted for SMTP — it will need refactoring tomorrow

**File:** `outreach_cli/commands/send.py:96-122`
**Issue:** The render-and-write loop hard-codes `write_eml(out_dir=preview_dir, ...)`. There is no `Transport` / `MailSink` abstraction. When Phase 2 adds SMTP:

- You will branch inside the loop: `if dry_run: write_eml(...) else: smtp.sendmail(...)` — quickly grows ugly.
- Or you will pass a `transport` callable. Better — but that's a refactor.
- The current return shape (`built: list[BuiltMail]`) couples successful sends with successful file writes. SMTP failures will need a different shape (delivered, deferred, bounced, …).

**Recommended fix (light touch, prepares Phase 2 without rewriting):**

```python
from typing import Protocol

class MailTransport(Protocol):
    def deliver(self, *, index: int, to_email: str, from_email: str,
                subject: str, body: str) -> BuiltMail: ...

class DryRunTransport:
    def __init__(self, preview_dir: Path):
        self.preview_dir = preview_dir
    def deliver(self, *, index, to_email, from_email, subject, body) -> BuiltMail:
        return write_eml(out_dir=self.preview_dir, index=index, to_email=to_email,
                         from_email=from_email, subject=subject, body=body)

# Phase 2 adds SmtpTransport with the same .deliver() shape.
```

Then `run_send` accepts `transport: MailTransport`. The CLI wires up which transport to use based on `--dry-run` / `--test-self` / `--confirm-live`. No branching inside `run_send`'s loop.

This is a 15-minute refactor *before* Phase 2 — much cheaper than doing it after SMTP code is also in `run_send`.

---

## MEDIUM

### MEDIUM-01: `outreach_cli/email/` collides with stdlib `email` package — works today, fragile tomorrow

**File:** `outreach_cli/email/__init__.py` (empty), `outreach_cli/email/builder.py:20-22`
**Issue:** Verified: `from email.mime.text import MIMEText` inside `outreach_cli/email/builder.py` resolves to stdlib because Python 3 uses absolute imports by default. No bug today.

But: if anyone ever adds `from __future__ import absolute_import` ... wait, that's the default. The real risk: if someone someday inserts a `from . import mime` or accidentally `import email.mime` somewhere that gets resolved via a different mechanism (zipped packages, custom finders, IDE refactor renaming `email` → relative). Also: static-analysis tools (pylint, pyright) sometimes get confused by name shadows and emit false positives.

**Recommended fix:** Rename `outreach_cli/email/` → `outreach_cli/mail/` or `outreach_cli/messaging/`. Costs 5 minutes today. Saves a future debugging session. The user-spec mandated the name but the spec was wrong — flag this to the user.

If the user refuses to rename, add a comment to `outreach_cli/email/__init__.py`:

```python
"""DO NOT add module-level imports here. This package shadows stdlib `email`
in name only — absolute imports of `email.mime.text` etc. still resolve to
stdlib because of Python 3 absolute-import default."""
```

### MEDIUM-02: `BuiltMail.path` typed as `Path | None` but the only constructor (`write_eml`) always sets it — except `build_eml` consumers don't set it at all

**File:** `outreach_cli/email/builder.py:31-37, 47-72, 75-99`
**Issue:** `BuiltMail.path` defaults to `None`. `build_eml` returns raw `bytes`, not a `BuiltMail`. `write_eml` always sets `path`. So in practice `BuiltMail.path` is never `None` when a `BuiltMail` exists.

This becomes painful in Phase 2: SMTP-delivered mails have no `.path`, but they still have all the other fields. The `Optional[Path]` is preparing for this — good — but the docstring/comments don't say so. A type-checker will require `b.path.name` in `cli.py:468` to be guarded.

Check `outreach_cli/cli.py:468`: `b.path.name`. If `path is None`, `AttributeError`. In Phase 1 this never happens (all `BuiltMail` come from `write_eml`). But the moment Phase 2 adds `SmtpDeliveredMail` via the transport, this becomes a latent crash.

**Recommended fix:** Tied to HIGH-04. When you introduce the Transport abstraction, also split `BuiltMail`:

```python
@dataclass(frozen=True)
class BuiltMail:
    to_email: str; subject: str; body: str; eml_bytes: bytes

@dataclass(frozen=True)
class DryRunDelivery:
    built: BuiltMail; path: Path

@dataclass(frozen=True)
class SmtpDelivery:
    built: BuiltMail; smtp_id: str; queued_at: datetime
```

`cli.py` then dispatches on type rather than calling `.path` blindly.

### MEDIUM-03: `_safe_filename` does not protect against collision when two emails differ only by special-char position

**File:** `outreach_cli/email/builder.py:40-44`
**Issue:** `_safe_filename("a.b@x.de")` and `_safe_filename("a_b@x.de")` both produce `"a_b_at_x.de"`. With `index` prefix this is unique within a single run (different `idx`), but the human-readable name is now ambiguous. Two leads with structurally similar emails get the same suffix.

**Recommended fix:** Append a short hash of the original email for disambiguation, or skip — the `idx` prefix already ensures filesystem uniqueness within a run. Acceptable as-is; flagging because it might surface as confusing duplicates in `preview/`.

### MEDIUM-04: `make_msgid(domain=from_email.split("@", 1)[-1])` fails open on malformed `from_email`

**File:** `outreach_cli/email/builder.py:65`
**Issue:** If `from_email = "georg"` (no `@`), `split("@", 1)[-1]` returns `"georg"` — `make_msgid` will use that as the domain, generating a non-RFC-compliant Message-ID like `<token@georg>`. Not a crash, but invalid.

If `from_email = ""`, `split("@", 1)[-1]` returns `""` — `make_msgid(domain="")` generates `<token@>` which IS a crash (some Python versions) or invalid output.

**Recommended fix:** Validate `from_email` at the entry point:

```python
def build_eml(*, to_email: str, from_email: str, subject: str, body: str) -> bytes:
    if "@" not in from_email or "@" not in to_email:
        raise ValueError(f"Invalid email: from={from_email!r}, to={to_email!r}")
    ...
```

### MEDIUM-05: `derive_render_vars` `{beispiel_keyword}` heuristic too fragile

**File:** `outreach_cli/leads/loader.py:101-102`
**Issue:** `primary_branche = branche.split("/")[0].strip()` then `f"{primary_branche} {stadt}"`. Failure modes:

- `BRANCHE = "/ Kosmetik"` → `primary_branche = ""` → `beispiel_keyword = " Bad Homburg"` (leading space). Renders to `"„ Bad Homburg"` in the email — visible glitch.
- `BRANCHE = "Kosmetik"` (no slash) → works, fine.
- `BRANCHE = "TCM / Akupunktur / Cupping"` → only `"TCM"` is used. Fine.
- `BRANCHE = "  / Kosmetik  /"` → `""` → glitch.

**Recommended fix:** Add a guard:

```python
primary_branche = branche.split("/")[0].strip()
if not primary_branche:
    # Fallback: try second segment
    parts = [p.strip() for p in branche.split("/") if p.strip()]
    primary_branche = parts[0] if parts else branche.strip()
if not primary_branche:
    raise ValueError(...)
beispiel_keyword = f"{primary_branche} {stadt}"
```

And add a test: `derive_render_vars` with `BRANCHE="/ Kosmetik"`.

### MEDIUM-06: `load_filtered_leads` `try/except Exception` swallows too much

**File:** `outreach_cli/leads/loader.py:133-140`
**Issue:** The `try` wraps `for lead in client.iter_tab_rows(tab)` and catches bare `Exception`. This catches `KeyboardInterrupt`-adjacent issues … no wait, `KeyboardInterrupt` is `BaseException`, not `Exception`, so that's fine. But it catches `MemoryError`, `RecursionError`, AND legitimate bugs in `iter_tab_rows` that should bubble up as bugs not as "Fehler beim Lesen von Tab X".

**Recommended fix:** Narrow to known gspread errors:

```python
from gspread.exceptions import APIError as GspreadAPIError, WorksheetNotFound
from ..sheets import SheetsAPIError

try:
    ...
except (GspreadAPIError, WorksheetNotFound, SheetsAPIError) as e:
    raise RuntimeError(f"Fehler beim Lesen von Tab {tab!r}: {e}") from e
```

### MEDIUM-07: `--include-hwg` flag name is confusing (semantic inversion)

**File:** `outreach_cli/cli.py:356-359, 406, 456-461`
**Issue:** Flag `--include-hwg` defaults `False` → HWG filter ON. To turn filter OFF, user passes `--include-hwg`. The negation is twice-confusing:

1. The name `include-hwg` reads as "include HWG entries" — but the default is *exclude* them, so the flag is conceptually a "disable filter" toggle.
2. Inside `run_send`, the parameter is `exclude_hwg=not include_hwg` — a double-negative.

Also: the rendering on line 456 `if not include_hwg:` is correct (when filter is ON we show stats) but reads like "if HWG-filter is excluded" which means the opposite. Easy to misread.

**Recommended fix:** Rename to typer's `--hwg-filter / --no-hwg-filter` idiom:

```python
hwg_filter: bool = typer.Option(
    True, "--hwg-filter/--no-hwg-filter",
    help="Heilpraktiker/Arzt-Filter (HWG). Default: AKTIV.",
),
...
exclude_hwg=hwg_filter,
...
if hwg_filter:
    typer.echo(f"  Nach HWG-Filter: {s.after_hwg}")
```

Reads naturally: "HWG filter is on by default; pass `--no-hwg-filter` to disable."

---

## LOW

### LOW-01: `Iterable` imported in `loader.py` but unused

**File:** `outreach_cli/leads/loader.py:15`
**Issue:** `from typing import Iterable, Optional` — `Iterable` never used.

**Fix:** Remove from import.

### LOW-02: Test docstring says "13 Tests" but file contains 13 numbered tests and the prompt says "18 tests"

**File:** `tests/test_send.py:3`
**Issue:** Comment in docstring: `"13 Tests gemäß User-Spec 2026-05-11"`. The file has 13 test functions numbered 1-13. The user prompt mentions "18 tests for send" — discrepancy somewhere (maybe more tests exist in another file, or the count is stale).

**Fix:** Update docstring to match actual count and add the missing scenarios (see LOW-05).

### LOW-03: `FilterStats.hwg_excluded` mutable default sidestepped via `__post_init__` — could use `field(default_factory=list)`

**File:** `outreach_cli/leads/loader.py:48-58`
**Issue:** Uses `hwg_excluded: list[str] = None` + `__post_init__` workaround. Standard Python idiom is `field(default_factory=list)`:

```python
from dataclasses import dataclass, field

@dataclass
class FilterStats:
    total_in_tab: int = 0
    after_score: int = 0
    after_status: int = 0
    after_hwg: int = 0
    after_limit: int = 0
    hwg_excluded: list[str] = field(default_factory=list)
```

Cleaner, no `# type: ignore` needed.

### LOW-04: `from_email = "georg@maxcontentseo.de"` hardcoded as CLI default

**File:** `outreach_cli/cli.py:372-374`, `outreach_cli/commands/send.py:51`
**Issue:** Owner email is a literal default. Fine for a single-owner tool, but a future contributor / co-owner will trip over it. Belongs in `Config` (already exists with env-driven loading).

**Fix:** Add `OWNER_EMAIL` env var (or `from_email` field) to `Config`, default fallback string for backward compat.

### LOW-05: Missing test coverage for several documented edge cases

**File:** `tests/test_send.py`
**Issue:** No tests for:

1. `TemplateNotFoundError` (template name that doesn't exist on disk).
2. `derive_render_vars` with empty STADT (raises ValueError) — what does `run_send` do? Currently crashes the whole batch (HIGH-03).
3. `derive_render_vars` with empty BRANCHE.
4. Lead with empty email (filtered out at line 136-137 of `loader.py`) — verify it doesn't end up in `built`.
5. `--no-dry-run` raises `NotImplementedError`.
6. `--test-self` / `--confirm-live` CLI flags reject with exit 2 (currently relies on the typer-level rejection but no test asserts it).
7. Status filter that matches zero leads (empty result).
8. Render error mid-batch: leads 1-3 render OK, lead 4 has a missing var, lead 5 renders OK → verify lead 5 still ends up in `built` and lead 4 in `skipped_render_errors`.

**Fix:** Add 5-8 tests covering the above. Especially (8) is important for the Phase-2 transition because SMTP partial-failure handling will follow the same pattern.

---

## Phase 2 Readiness — Verdict: NEEDS-REFACTOR-BEFORE-SMTP

**What works for Phase 2 as-is:**
- Filter pipeline (`load_filtered_leads`) is reusable unchanged.
- Template engine is transport-agnostic — perfect.
- `build_eml` produces RFC-822 bytes ready to `sendmail` (once BOM is stripped — CRITICAL-02).
- CLI flag scaffolding for `--test-self` / `--confirm-live` is already in place.

**What needs refactoring before SMTP code lands:**
1. **HIGH-04 (Transport abstraction):** Introduce `MailTransport` protocol. `run_send` should not branch on `dry_run` internally — that becomes unmaintainable once a third mode (`--test-self`) is added.
2. **CRITICAL-02 (BOM):** Strip BOM from `build_eml`. SMTP wire-protocol does not tolerate it cleanly.
3. **MEDIUM-02 (BuiltMail.path):** Split delivery-result type so SMTP results don't carry a meaningless `path` field.
4. **HIGH-03 (per-lead robustness):** SMTP will have per-lead failures (transient bounces, greylisting). The current "raise on first bad lead" semantics in `load_filtered_leads`/`derive_render_vars` will hurt — fix the dry-run behavior first, SMTP inherits it.

**Cost estimate:** 60-90 minutes for items 1-4 before writing any SMTP code. Cheaper than the alternative (writing SMTP, then realizing the abstraction is wrong, then unwinding).

---

_Reviewed: 2026-05-11_
_Reviewer: Claude (Opus 4.7, gsd-code-reviewer)_
_Depth: deep (cross-file: loader → engine → builder → cli → tests)_
