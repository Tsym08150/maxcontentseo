---
project: outreach-cli
reviewed: 2026-05-11T09:03:00+02:00
depth: deep
files_reviewed: 10
files_reviewed_list:
  - outreach_cli/config.py
  - outreach_cli/sheets.py
  - outreach_cli/cli.py
  - outreach_cli/__main__.py
  - outreach_cli/__init__.py
  - tests/test_sheets.py
  - pyproject.toml
  - .env.example
  - .gitignore
  - README.md
findings:
  critical: 3
  high: 6
  medium: 8
  low: 7
  total: 24
status: issues_found
---

# outreach-cli Code Review

**Stance:** adversarial. Assumed defects exist; surfaced what can be proven from source.

---

## Summary

24 findings: 3 CRITICAL, 6 HIGH, 8 MEDIUM, 7 LOW.

The header-alias system has a **silent wrong-column-match bug** in `_write_status_for_lead` (CR-01) that can write the date into the wrong cell when an alias-canonical-key is requested. `set_status` has **no rollback** on partial-failure mid-update (CR-02), and the **fallback-to-`KONTAKTIERT_AM`** branch can clobber the outreach contact date with the answer date (CR-03). The `.env.example` ships a **real-looking `SHEET_ID`** (HIGH-01). Other issues include broken inconsistency-warning logic for missing canonical columns, `find_by_email` not catching auth errors, idempotency edge cases, and missing tests for the entire mutation layer.

## Top 3 Critical

1. **CR-01** — `_write_status_for_lead` requests `_find_header(headers, status_column)` where `status_column ∈ {Verkaufsstatus, Recherche_Status}`. These have no aliases, so it's safe today, BUT the same function uses `_find_header` for the date columns which DO have aliases. If a Stadt-Tab has the alias header (e.g. `FOLLOW-UP`) but `_find_header` matches it for `H_FOLLOWUP`, the write target is the alias column — correct intent. However on `Alle_Leads` (alias `Stadt` for `STADT`), `_find_header` returns the alias index. That part works. The real bug: `_find_header` uses `lower()` only — `'KONTAKTIERT AM'` (alias, with space) and `'KONTAKTIERT_AM'` (canonical) are NOT equal under `.lower()` alone, so on a sheet that has BOTH `KONTAKTIERT` (alt) AND `KONTAKTIERT_AM` (canonical), alphabetical/positional priority decides — but order of candidates is `[name] + aliases`, so canonical wins. OK on read side. **However**, on the inconsistency-warn block in `set_status` (sheets.py:394-401), `primary.data.get(column, "")` uses RAW dict access — if the canonical key is absent (which `_normalize_row` only fixes for the four aliased headers — Verkaufsstatus and Recherche_Status are NOT in the alias map), and a tab uses some other spelling, the warning silently compares `"" != ""` → no warning. **A real wrong-update can go unnoticed.**

2. **CR-02** — `set_status` writes primary first, then secondary, with no atomicity (sheets.py:403-411). If the secondary write throws (network blip, quota, lost permission), the caller sees a Python exception bubble up from `cli.py:215`, but **the primary tab has already been mutated** and the cache invalidated. There is no rollback and no recorded "partial success" state. Worse: the CLI's broad `except Exception` (cli.py:218) emits "API-FEHLER" and exits 2, hiding the fact that primary is now updated and secondary is stale — exactly the inconsistency the warning system is meant to catch, now created BY the tool itself.

3. **CR-03** — Fallback logic at sheets.py:348-356 is buggy. When the status routes to `LETZTE_ANTWORT_AM` AND that column is missing, it falls back to `KONTAKTIERT_AM`. This means setting `"Bounce"` or `"Geantwortet - kein Interesse"` on a sheet without `LETZTE_ANTWORT_AM` **overwrites the original outreach date** with the bounce/answer date. Silently. Worse: the test suite has zero coverage of `_write_status_for_lead`, so this branch has never been exercised. The README documents this as intended behaviour, but documentation does not absolve data corruption — the user's "when was this lead first contacted?" history is lost.

---

## CRITICAL

### CR-01 — Inconsistency-warn block uses raw dict access; misses true inconsistency (BLOCKER)

**File:** `outreach_cli/sheets.py:394-401`
**Issue:** `primary.data.get(column, "")` where `column` is `"Verkaufsstatus"` or `"Recherche_Status"`. These canonical names are NOT in `HEADER_ALIASES`, so `_normalize_row` does not enrich the dict with them when the sheet uses a different spelling. If any tab (existing or future) has e.g. `Verkaufs_Status`, `verkaufsstatus` (lowercase), or any drift, the lookup silently returns `""` for both primary and secondary, the warning never fires, and the inconsistency is hidden — yet the write proceeds via `_find_header` which DOES find the column. Net effect: user gets "OK" with no warning while two different starting values were silently overwritten.
**Fix:** Use header-aware lookup, not raw dict:
```python
def _lead_status_value(lead: LeadRow, column: str) -> str:
    # Re-resolve via headers, not just dict key
    for key, val in lead.data.items():
        if key.strip().lower() == column.strip().lower():
            return val.strip()
    return ""
p_val = _lead_status_value(primary, column)
s_val = _lead_status_value(secondary, column)
```
Better: add `H_VERKAUFSSTATUS` and `H_RECHERCHE_STATUS` to `HEADER_ALIASES` with plausible drift candidates, OR have `_normalize_row` enrich any header that fuzzy-matches a canonical name.

### CR-02 — `set_status` has no atomicity / partial-failure handling (BLOCKER)

**File:** `outreach_cli/sheets.py:403-411`
**Issue:** Loop `for lead in (primary, secondary)` writes sequentially. If `_write_status_for_lead` raises on `secondary` (network, 429 quota, permission revoked, race with another writer), the primary is already mutated. No try/except, no rollback, no result-with-partial-success. The CLI then catches the exception with `except Exception` at cli.py:218, emits a single red "API-FEHLER" line, exits 2. Caller has no idea primary was successfully written and secondary is now stale.
**Fix:**
```python
results = []
for lead in (primary, secondary):
    if lead is None: continue
    try:
        dc, dv, ws_ = self._write_status_for_lead(lead, status, column, when)
        warnings.extend(ws_)
        results.append(("ok", lead, dc, dv))
    except Exception as e:
        warnings.append(f"[{lead.tab}] WRITE FAILED: {e!r} — andere Tabs ggf. bereits aktualisiert.")
        results.append(("fail", lead, None, None))
# Pick first successful date metadata; surface partial state in SetStatusResult
```
Add a `partial_failure: bool` field to `SetStatusResult`; CLI should exit 3 (new code) on partial.

### CR-03 — `KONTAKTIERT_AM` overwritten by answer date when `LETZTE_ANTWORT_AM` missing (BLOCKER)

**File:** `outreach_cli/sheets.py:348-356`
**Issue:** Fallback silently overwrites the original outreach-date with today's response-date. Setting `"Bounce"` on a Stadt-tab whose `LETZTE_ANTWORT_AM` was never added clobbers the lead's KONTAKTIERT_AM timestamp. The audit trail "when did we first reach out?" is destroyed. Schema migration is supposed to have unified the tabs, but `_normalize_row` does not inject `LETZTE_ANTWORT_AM` as an alias-target (there's no entry for `H_ANTWORT` in `HEADER_ALIASES`), so any Stadt-tab still missing this column triggers the destructive fallback. README documents this; that does not make it correct.
**Fix:** Remove the destructive fallback. Either:
1. Refuse to write the date and add a HARD warning ("kann LETZTE_ANTWORT_AM nicht schreiben — Spalte fehlt in tab X") and let the human add the column;
2. Auto-add the column with `ws.add_cols(1)` + header-cell-write. Option 1 is safer.
```python
if col is None and date_header == H_ANTWORT:
    warnings.append(
        f"[{lead.tab}] LETZTE_ANTWORT_AM-Spalte fehlt — Datum NICHT geschrieben. "
        f"Spalte manuell ergänzen, sonst geht das Antwort-Datum verloren."
    )
    # do NOT fall back; date_col_used stays None
```

---

## HIGH

### HI-01 — Real-looking SHEET_ID committed in `.env.example`

**File:** `.env.example:5`
**Issue:** `SHEET_ID=<real-google-spreadsheet-id>` — a real-looking Google Spreadsheet ID was committed as the example value, not a placeholder. *(Redacted on 2026-05-15 in security-fix; original value rotated/scrubbed before public release.)* If it IS the production sheet, anyone with read access to the repo plus the (separately-distributed) service-account JSON can read/write the lead database. Even if the JSON is properly secret, the ID is a piece of information that narrows attack surface considerably. The placeholder pattern is `SHEET_ID=your-spreadsheet-id-here`.
**Fix:** Replace with placeholder; document the real ID in private notes / 1Password. Also check git history — if previously committed, the ID is already public.
```ini
SHEET_ID=REPLACE_WITH_YOUR_SPREADSHEET_ID
```

### HI-02 — `find_by_email` swallows only `WorksheetNotFound`; auth/network errors propagate raw

**File:** `outreach_cli/sheets.py:244-252`
**Issue:** Inside the linear scan, only `gspread.exceptions.WorksheetNotFound` is caught. On `gspread.exceptions.APIError` (429 quota, 401 token revoke, 5xx), the loop dies after a partial scan with a raw exception bubbling to the CLI catch-all, displayed as "API-FEHLER: APIError: ...". User cannot tell whether scan finished without finding the lead or aborted midway. For `set_status` this is critical: a failed lookup could lead the tool to claim "Lead nicht gefunden" (exit 1) when in reality the lead exists but quota blocked the read of a later tab.
**Fix:** Differentiate transient API errors. Re-raise APIError with context, or wrap into a domain exception:
```python
except gspread.exceptions.APIError as e:
    raise RuntimeError(f"API-Fehler beim Lesen von Tab {tab!r}: {e}") from e
```
Currently `set_status` does `find_by_email` AND `find_in_aggregate` before writing — if the first succeeds and second throws on quota, you write only to primary and don't touch secondary, drifting the two tabs. (Related to CR-02.)

### HI-03 — `_find_header` alias precedence can match canonical-of-other-field

**File:** `outreach_cli/sheets.py:54-66`
**Issue:** `HEADER_ALIASES[H_KONTAKTIERT] = ("KONTAKTIERT", "KONTAKTIERT AM", "Kontaktiert")`. When called for `H_KONTAKTIERT`, candidates are `["KONTAKTIERT_AM", "KONTAKTIERT", "KONTAKTIERT AM", "Kontaktiert"]`. Fine. But: if a Stadt-Tab has BOTH `KONTAKTIERT` (alt) and `KONTAKTIERT_AM` (canonical) — a real possibility during the migration window — the canonical wins (correct). Now consider `_find_header(headers, H_FOLLOWUP)` on a sheet that has columns `FOLLOWUP_AM` AND `FOLLOW-UP` (orphaned alt-column the migration forgot): canonical wins on read but in `_write_status_for_lead`, the WRITE target is also `FOLLOWUP_AM` — so writes orphan the alt column silently, growing stale data. Worse, `hot_leads` reads `lead.followup_am` which via `_normalize_row` only enriches if canonical is ABSENT — so the canonical-present case ignores the alt column. If migration was partial and alt has data while canonical is empty, `followup_am` returns "" and the lead is invisible to `hot_leads` and `followups_on`.
**Fix:** Add a "schema-doctor" subcommand that detects duplicate canonical+alias columns and warns. At minimum, `_normalize_row` should warn (via logger) when both are present with different values.

### HI-04 — `followups_on` requires exact (case-insensitive) stadt match — silent miss on partial typos

**File:** `outreach_cli/sheets.py:264-281`
**Issue:** `_match_tab` does `t.lower() == stadt.lower()`. Pass `--stadt frankfurt-umland` (hyphen vs underscore) → `tab_match = None` → scans ALL primary tabs and tries `lead.stadt.lower() == stadt.lower()` (sheets.py:277) which also fails. Returns empty list silently. User assumes "no followups today". Same for `--stadt bad-homburg` vs `Bad Homburg`. Exit 0 with no error.
**Fix:** If `tab_match is None`, validate against `config.primary_tabs` and fail loud:
```python
if tab_match is None:
    valid = ", ".join(self.config.primary_tabs)
    raise ValueError(f"Unbekannte Stadt {stadt!r}. Gültig: {valid}")
```
Or fuzzy-match and confirm.

### HI-05 — `hot_leads` filter: `fu < today` excludes today, but logic comment says "≥ heute"

**File:** `outreach_cli/sheets.py:300-301`
**Issue:** Code: `if fu is None or fu < today: continue` → excludes only strictly-past dates, includes today. Docstring says `FOLLOWUP_AM >= heute`. Consistent — OK. But the `if fu is None` branch also drops leads with **unparseable** dates, including alternate formats not in the parser's allowlist. That includes leads with date written as `11. Mai 2026` (German prose), serial numbers (Google Sheets occasionally returns date-as-number when `value_input_option` differs), or trailing-noise like `11.05.2026 (vermutet)`. Such leads are silently invisible to hot-detection.
**Fix:** Log a count of unparseable-date skips; consider adding a verbose flag. Add `%d. %b %Y` and German month names to `_parse_date`.

### HI-06 — `set_status` re-fetches after writes using the same `find_by_email` that may now have stale cache

**File:** `outreach_cli/sheets.py:413-415`
**Issue:** After writes, `find_by_email` is called again. `_write_status_for_lead` calls `_invalidate(lead.tab)` (sheets.py:365) for the written tab. Good — both tabs were invalidated if both were written. But: there's a TOCTOU race between write and re-fetch. If another writer (another CLI invocation, Apps Script, manual edit) modifies the row between batch_update and re-fetch, the SetStatusResult shows mismatched values. Not catastrophic (re-fetch is informational), but the CLI prints those values as "OK confirmed" — misleading. Also, the re-fetch is two extra full-tab reads = doubles API quota cost per `set-status` call.
**Fix:** Drop the re-fetch; mutate the in-memory LeadRow with the new values and return that:
```python
def _with_updated(lead, column, status, date_col, date_val):
    new = dict(lead.data); new[column] = status
    if date_col and date_val: new[date_col] = date_val
    return LeadRow(tab=lead.tab, row_index=lead.row_index, data=new)
```

---

## MEDIUM

### ME-01 — `Config.from_env` raises `SystemExit` from a library module

**File:** `outreach_cli/config.py:94, 96, 100, 105`
**Issue:** Raising `SystemExit` from a non-`__main__` module makes the function untestable without subprocess and pollutes the call stack. `cli.py:216` even has `except SystemExit: raise` to defend against this leakage. That's a code smell pointing at this exact bug.
**Fix:** Define `class ConfigError(Exception): pass`; raise that; let `cli.py` catch + format + exit. Easier: `typer.BadParameter` is not appropriate here, so a custom exception is correct.

### ME-02 — `load_dotenv` runs at import time with a fixed path

**File:** `outreach_cli/config.py:12-13`
**Issue:** `_DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"` — assumes the user invokes from project-relative location and that `.env` lives next to `outreach_cli/`. Editable-installs fine; pip-installed-to-site-packages → `_DOTENV_PATH` points inside `site-packages/.env` which doesn't exist, and `load_dotenv` silently returns `False`. User then gets the "SHEET_ID fehlt" error and no hint why.
**Fix:** Try CWD first, then module-parent, log which file was loaded. Or accept `OUTREACH_CLI_ENV` env var override.

### ME-03 — `SetStatusResult.warnings` field is `list[str]` but dataclass is `frozen=True`

**File:** `outreach_cli/sheets.py:177-186`
**Issue:** Frozen dataclass with a mutable list field. The list itself is mutable — `frozen=True` only prevents reassignment of the field, not mutation. Misleading. `warnings.extend(...)` in callers (sheets.py:407) mutates the list. Plus: frozen dataclasses make `hash(SetStatusResult)` raise because of unhashable fields. Not a bug here, but a brittle pattern.
**Fix:** Either drop `frozen=True` or use `tuple[str, ...]`.

### ME-04 — `Optional[Iterable[str]]` parameter consumed twice / once?

**File:** `outreach_cli/sheets.py:234-243`
**Issue:** `tabs: Optional[Iterable[str]]`. Caller could pass a generator that's already been consumed; the code does `list(tabs)` so it's OK once. But if `tabs=()` is passed explicitly, the function returns `None` (no scan) without warning — silent behaviour change. Document or assert non-empty.
**Fix:** Type as `Optional[Sequence[str]]`; assert non-empty when supplied.

### ME-05 — Zero unit-test coverage of mutation path

**File:** `tests/test_sheets.py` (whole file)
**Issue:** All 34 tests target pure-logic helpers. `_write_status_for_lead`, `set_status`, the inconsistency-warn branch, the LETZTE_ANTWORT_AM fallback, the partial-failure path — none tested. The most dangerous code is uncovered. A `gspread`-mock with `unittest.mock` would cover this cheaply.
**Fix:** Add `tests/test_set_status.py` with a `FakeWorksheet` and a `FakeSpreadsheet` injected into a `SheetClient` (extract `_gc`/`_sh` setup behind a factory method to enable injection).

### ME-06 — `cli.py` catch-all `except Exception` masks programmer errors

**File:** `outreach_cli/cli.py:95, 128, 218, 271`
**Issue:** Every command wraps the client call in `except Exception`. AttributeErrors, KeyErrors, TypeErrors in the wrapper code all become red "API-FEHLER" lines. Debugging is hard. Should catch `gspread.exceptions.APIError` and `RuntimeError` specifically; let real bugs raise + show traceback.
**Fix:**
```python
except (gspread.exceptions.APIError, gspread.exceptions.GSpreadException) as e:
    typer.secho(f"API-FEHLER: {e}", fg="red", err=True); raise typer.Exit(2) from e
```

### ME-07 — `--date` parsing inconsistent between commands

**File:** `outreach_cli/cli.py:47-58, 212`
**Issue:** `_parse_iso` exists, but `set-status` does `when = _parse_iso(date_) if date_ else date.today()`. Both branches end at `date.today()` because `_parse_iso(None)` returns today. The redundant `if date_ else` is dead and confusing — it suggests the two branches differ.
**Fix:** `when = _parse_iso(date_)`.

### ME-08 — `_emit_json` no type-hint on payload, single-line output not indented

**File:** `outreach_cli/cli.py:77-78`
**Issue:** Pipeable output is fine, but the README's "JSON-Output" example shows multi-line pretty-printed JSON. Disagreement between docs and behaviour. Plus the function signature `_emit_json(payload)` has no type annotation, undermining the file's `from __future__ import annotations`.
**Fix:** Add `--pretty` flag or accept it's compact-only and update README. Type as `payload: object`.

---

## LOW

### LO-01 — `_DOTENV_PATH` doesn't check `cwd` (user reported issue likely)

**File:** `outreach_cli/config.py:12`
**Issue:** See ME-02. Listed again as LOW because the dominant invocation pattern is `cd outreach-cli && py -m outreach_cli ...` which works.

### LO-02 — Emoji `⚠` in stderr output may break on cp1252 Windows consoles

**File:** `outreach_cli/cli.py:175, 248`
**Issue:** `sys.stdout.reconfigure(encoding="utf-8")` is wrapped in `try/except` and only affects stdout. The `typer.secho(..., err=True)` writes to STDERR. On a non-reconfigured stderr the `⚠` raises `UnicodeEncodeError`. The user has prior pain with PS5.1 UTF-8 issues (per MEMORY.md). Same fix needed for stderr.
**Fix:**
```python
for stream in (sys.stdout, sys.stderr):
    try: stream.reconfigure(encoding="utf-8")
    except Exception: pass
```

### LO-03 — `__main__.py` has unreachable `__name__ == "__main__"` check

**File:** `outreach_cli/__main__.py:5-6`
**Issue:** When invoked via `python -m outreach_cli`, `__main__.py`'s `__name__` is `"__main__"`, so the guard is correct but redundant — the file's only purpose is to be that entry point. Imported elsewhere it would just import `main`, no harm.
**Fix:** Style only — keep or remove. Either is fine.

### LO-04 — `H_RECHERCHE_STATUS` and `H_VERKAUFSSTATUS` not in `HEADER_ALIASES`

**File:** `outreach_cli/config.py:48-53`
**Issue:** Migration normalized these, but the alias map only protects FIRMA/STADT/dates. Any future drift in status-column naming silently fails (related to CR-01).
**Fix:** Add empty-tuple entries with explanatory comment, or document that these columns are migration-locked.

### LO-05 — `idempotency`: re-running `set-status` with same args triggers an extra batch_update even when value unchanged

**File:** `outreach_cli/sheets.py:335-365`
**Issue:** No diff before write. Calling `set-status --status Bounce` twice writes "Bounce" twice. Quota cost and API noise. Not data-corrupting, but wasteful.
**Fix:** Skip the write if `lead.data.get(status_column) == status` AND date already matches. Add `--force` to override.

### LO-06 — `_parse_date` accepts ambiguous DD/MM and YYYY-MM-DD without disambiguation

**File:** `outreach_cli/sheets.py:101`
**Issue:** `%d/%m/%Y` is locale-ambiguous; `01/05/2026` → 1. Mai 2026 here, but a US user would expect 5. Januar. Since the project is DE-only, OK, but worth documenting.
**Fix:** Document or drop `%d/%m/%Y` (it's not used anywhere in the sheets).

### LO-07 — `Iterable` imported but `Sequence`/`Iterator` are more accurate

**File:** `outreach_cli/sheets.py:14`
**Issue:** `iter_tab_rows` returns `Iterable[LeadRow]` but is a generator → `Iterator[LeadRow]`. `find_by_email`'s `tabs: Optional[Iterable[str]]` is converted to list; should be `Sequence[str]` to disallow consumed-generators.
**Fix:** Type narrowing.

---

## Test-Coverage Gaps (summary, see ME-05)

- `_write_status_for_lead` — full path uncovered
- `set_status` aggregate-sync (primary-only, secondary-only, both)
- Inconsistency-warn branch (CR-01 lives here)
- LETZTE_ANTWORT_AM-missing → KONTAKTIERT_AM fallback (CR-03 lives here)
- `find_by_email` over missing tab (WorksheetNotFound skip)
- `hot_leads` with bad SCORE values, bad date values
- `followups_on` with unknown stadt
- `Config.from_env` missing/malformed paths
- CLI exit-codes (typer's `CliRunner` supports this trivially)

---

_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
_Adversarial stance maintained throughout. Findings classified by data-loss/security/correctness/quality severity._
