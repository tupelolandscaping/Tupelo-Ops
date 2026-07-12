---
title: Cross-Reference/Auto-Sync Audit — Repo-Wide Dependency Catalog
type: planning
status: draft — awaiting owner sign-off on Section 5 open decisions
date: 2026-07-10
tags: [audit, cross-reference, planning, follow-up-22]
---

# Cross-Reference/Auto-Sync Audit — Repo-Wide Dependency Catalog

**Purpose.** Scopes Follow-Up #22 (`CONTEXT.md`): catalog every place one file or value in this repo depends on another's current state, and classify each dependency by whether it's actually safeguarded. **This is a catalog and classification pass, not a fix pass** — every dependency below was checked against the real, current repo state (scripts run, files diffed, values cross-read), not assumed from memory. No code was changed, no ledger was edited, nothing was fixed. Mirrors `PHASE7-PLAN.md`/`PROJECTION-PLAN.md`'s structure and discipline.

---

## 1. Scope re-read (Step 1)

Re-read Follow-Up #22 and H-051 fresh before cataloging anything new. H-051's finding, restated precisely because it's this whole audit's precedent: `model/parse_invoices.py` regenerated `revenue-invoices.csv`/`revenue-line-items.csv` from a fresh PDF, but nothing regenerated `ledger-revenue.csv`'s 319 `event=invoice` rows from that fresh parse — `match_payments.py`'s own docstring explicitly disclaimed touching invoice-side rows, so the actual ledger the model builds from could go stale after a routine revenue refresh, silently, with no error. That is the shape of gap this audit hunts for: **a real dependency with no automated check and no accurate documentation**, discovered only by deliberately tracing what each script reads and writes rather than trusting a script's name or its docstring's stated intent.

Follow-Up #22's four named starting-point examples (not the full list): `assumptions.csv` TARGET/POLICY rows on `strategy/`/`CONTEXT.md`; `RUNBOOK.md` checkboxes on `HISTORY.md`; `reference/README.md`'s active-snapshot pointers on the files they point to; `CONTEXT.md` Follow-Up statuses on the ledger's actual state.

---

## 2. Dependency catalog (Steps 2–3)

Each entry: the dependency, what was actually checked (not assumed), and its classification — **(a)** automated/fail-closed, **(b)** documented/manual/accurate, **(c)** undocumented gap, **(d)** documented but stale.

### 2.1 The `*-UPDATE.md` procedures vs. the scripts they describe

| Procedure | Checked against | Result |
|---|---|---|
| `reference/CATALOG-UPDATE.md` | `model/parse_invoices.py`, `model/build_ledger_revenue.py` | **(d) STALE.** Step 7 says "Re-run `python model/parse_invoices.py` and confirm all gates still pass" — it does not mention running `model/build_ledger_revenue.py`. This is the *exact same gap H-051 found and fixed in `REVENUE-UPDATE.md`*, left unfixed here: a catalog refresh can change how existing lines classify (service vs. `BLOCKED — unmapped`, or `item`/`service` kind) once re-parsed, and without the ledger-rebuild step, `ledger-revenue.csv` stays stale exactly the way H-051 already demonstrated it can. |
| `reference/REVENUE-UPDATE.md` | `model/parse_invoices.py`, `model/build_ledger_revenue.py`, `model/refresh_all.py` | **(b) Accurate.** Re-read fresh: steps 1–8 match the scripts' actual current behavior exactly, including the H-051 fix (step 6) and a pointer to `refresh_all.py` as the simpler alternative. |
| `reference/PAYROLL-UPDATE.md` | `model/populate_labor_from_payroll.py`, `model/reconcile_payroll_relay.py` | **(d) STALE / factually misleading, a new finding.** Step 5 says a new employee not found in the role map should be added "to `model/data/employee-role-map.csv`" — but that file is **fully overwritten every run** by `write_role_map()` from the hardcoded `ROLE_MAP_ROWS` list inside the script itself (confirmed by direct code inspection: `write_role_map()` is called unconditionally in `main()`). Following this instruction literally — editing the CSV directly — would have the edit silently discarded the next time the script runs, and the exact same `GATE FAILED` error would recur. The script's own error message is correct ("add them to ROLE_MAP_ROWS"); the doc's is not. Everything else in this procedure (steps 1–4, 6–12) was checked and is accurate. |

### 2.2 Pipeline stages' read/write contracts (per `README.md`'s pipeline / `model/refresh_all.py`)

Traced directly from each script's own path constants, not recalled:

| Script | Reads | Writes | Assumed-without-enforcement by anything else? |
|---|---|---|---|
| `parse_invoices.py` | `reference/invoices_*.pdf` (newest by filename), `service-name-map.csv`, `catalog-type-map.csv`, the active catalog snapshot via `reference/README.md`'s pointer | `revenue-invoices.csv`, `revenue-line-items.csv` | No — its own fail-closed gates (a) cover the catalog/service-map dependency. |
| `build_ledger_revenue.py` | `revenue-line-items.csv`, `revenue-invoices.csv` | `ledger-revenue.csv` (invoice/surcharge/tip rows only) | No — has its own fail-closed anchor gate (a). |
| `match_payments.py` | `reference/Relay*.csv`, `revenue-invoices.csv` | `ledger-revenue.csv` (payment rows only), `ledger-overhead.csv` (Stripe fee rows only) | No — has its own fail-closed classification gate (a). |
| `populate_step4.py` | `reference/Relay*.csv` (via `match_payments.load_relay_rows()`) | `ledger-overhead.csv` (remaining categories), `ledger-materials.csv`, `ledger-capital.csv` | No — has its own fail-closed capital-rows gate (a, H-051). |
| `populate_labor_from_payroll.py` | `reference/tupelo-landscaping-llc-payroll-summary-*.csv`, `ROLE_MAP_ROWS` (hardcoded in the script) | `employee-role-map.csv` (fully overwritten from `ROLE_MAP_ROWS`), `ledger-labor.csv`, `ledger-overhead.csv` (tax-burden rows) | **See 2.1's PAYROLL-UPDATE.md finding** — `employee-role-map.csv` is a derived artifact, not an independent source, and this isn't documented as clearly as it should be anywhere except the script's own error message. |
| `reconcile_payroll_relay.py` | `reference/tupelo-landscaping-llc-payroll-summary-*.csv`, `reference/Relay*.csv` | Console only, no file writes | No — has its own fail-closed `KNOWN_EXCEPTIONS` gate (a). |
| `build_model.py` | All five `ledger-*.csv`, `assumptions.csv` | `financial-model.xlsx` (gitignored) | No — has its own fail-closed revenue-anchor gate (a). |

**No orphaned assumption found here beyond the two already listed in 2.1** — every script's output either has its own fail-closed check, or (for `employee-role-map.csv`) the gap is really a documentation-accuracy problem already caught above, not a new independent one.

### 2.3 `assumptions.csv`'s TARGET/POLICY rows vs. their cited sources — checked individually, all 18 rows

| Row | Cited source | Checked fresh | Result |
|---|---|---|---|
| `peak_revenue_target` | `CONTEXT.md` Section 3 | Re-read Section 3: still states ~$10,000/month | **(b)** in sync |
| `cash_buffer_reserve`, `cash_buffer_truck_hedge` | `strategy/execution-timeline.md` Cash Buffer Policy | Re-read: $4,000 + $2,000 unchanged | **(b)** in sync |
| `cash_starting_balance` | `HISTORY.md` H-039 | $1,225.33, 2026-07-06 — unchanged since | **(b)** in sync (Follow-Up #21 already tracks its future re-verification need) |
| `konji_hourly_rate` (3 rows) | `HISTORY.md` H-048, `CONTEXT.md` D4 | Correctly reflects the **corrected** $20/hr-current / $25/hr-post-switch facts — built from the already-corrected H-048 finding, not the stale one | **(b)** in sync — *but see 2.5 below*, the SOURCE this cites (`CONTEXT.md` D4) is correct; a **different** document (`strategy/strategic-plan.md`) still contradicts it |
| `konji_revenue_share_pct` | `CONTEXT.md` D3/D4 | 6%, Sep 2026–May 2027 — unchanged | **(b)** in sync |
| `konji_canvassing_rate`, both bonuses, `konji_winter_project_rate` | `strategy/strategic-plan.md` Section 4 | Re-read Section 4 (Labor & Org Plan, line 141) directly: $15/hr, $15/fall client, $20/spring client, $25/hr winter — all match exactly | **(b)** in sync on the numbers *(but see 2.5 — the same source line also carries a stale claim these specific figures don't depend on)* |
| `xavier_payout`, `owner_truck_debt_repayment` | `CONTEXT.md` Section 6 item D / `strategy/strategic-plan.md` Section 6 Phase 3 | $1,800 / $3,800, sequencing unchanged | **(b)** in sync |
| `anais_canvassing_rate`, `anais_backup_lead_rate` | `CONTEXT.md` Follow-Up #11 | Re-checked `strategy/strategic-plan.md` Section 4 directly: still only "$/hr + per-sale" (a formula placeholder, no number) | **(b)** in sync — BLOCKED status still correct |
| `crew_labor_model` | `CONTEXT.md` D2 (reframed H-049) | Reference-only row, explicitly not consumed by the calc | **(b)** in sync |
| `revenue_growth_rate_assumption` | `model/PROJECTION-PLAN.md` Section 2.3 | 75.9%, matches; label correctly documents Decision 11's resolution (H-053) | **(b)** in sync |

**Every `assumptions.csv` row is currently in sync with what it cites.** The one real problem in this whole area isn't in `assumptions.csv` — it's that one of its correct source documents (`CONTEXT.md` D4) has a duplicate elsewhere (`strategy/strategic-plan.md`) that was never corrected. See 2.5.

### 2.4 `RUNBOOK.md` checkboxes vs. `HISTORY.md`

Checked Phase 0–8's "Done when" lines and the individual Phase 5/7 item boxes against current `HISTORY.md` entries and repo state:

- Phases 0–6, 8: all checked entries' cited H-numbers and commits still match current repo state; Phase 8's "check-in cadence has not yet resumed" re-verified directly (`check-ins/` still contains only the template).
- Phase 7: content is accurate (this session already fixed this class of drift three times — H-040, H-050, H-051). One **cosmetic** staleness remains: the "Done when" parenthetical reads *"2026-07-10 sync, this pass: ... H-046–H-049"* — five more passes (H-050 through H-054) have happened since, and "this pass" no longer identifies which one. Not factually wrong (H-046–H-049 are still accurate citations for what they cover), just dated phrasing. **(d), cosmetic only.**

### 2.5 `strategy/strategic-plan.md` vs. `CONTEXT.md` D4 — a real, previously-uncaught factual drift

**The most significant finding in this audit.** `CONTEXT.md` D4 was corrected in H-048 with an explicit strikethrough: Konji's rate was **not** "$25/hr base from day one" — real payroll data shows $20/hr for all 20 of his real completed pay periods, with $25/hr taking effect only from his next (not-yet-run) period. `strategy/strategic-plan.md` Section 4, line 141, states the exact same underlying fact — **and still reads "$25/hr base from day one," uncorrected**, with no strikethrough, no note, nothing. Verified fresh (not recalled): the line was re-read directly, in full, this pass. Two documents describing the same fact now disagree, and nothing flags it. This is exactly the H-051-class failure mode Follow-Up #22 exists to catch, just in prose rather than in a script/ledger pair.

**(d) documented but stale** — though "documented" undersells it; this is a direct factual contradiction between two supposedly-authoritative documents, not merely an outdated procedure.

### 2.6 `reference/README.md`'s active-snapshot pointers and account map

- **Catalog pointer** (`service-catalog-2026-07-09.csv`): file exists, matches. **(b)**
- **Payroll files list**: both listed files exist, dates match, no third file has been added since (confirmed via `ls`). **(b)**
- **Relay account map** (8735/3549/3550/8737/8736): cross-checked against `CONTEXT.md`'s own restated copy — the two are explicitly documented as a "linked pair" (`reference/README.md` line 48) and are currently identical. **(b)**

### 2.7 `CONTEXT.md` Follow-Up statuses vs. actual repo state

Spot-checked the Follow-Ups most likely to have quietly resolved themselves the way #14 did (checked against `ledger-overhead.csv`, `strategy/strategic-plan.md`, and script source directly, not assumed): **#11** (Anais's rates — still only a formula placeholder, `strategy/strategic-plan.md` Section 4, confirmed BLOCKED is still correct), **#17** (Homeworks-direct card fee — `ledger-overhead.csv` still has no such category beyond Stripe's 32 rows, confirmed still BLOCKED), **#18** (the $38.16 unclassified Stripe debit — no reference to it found anywhere in `model/*.py` beyond the existing exclusion, still open). **No additional stale Follow-Up found** beyond #14 (already fixed, H-051). This list is being actively, correctly maintained. **(b)** across the board.

### 2.8 `CLAUDE.md`'s own rules vs. actual current script behavior

The "every data-quality script fails closed" claim (H-051) was **not** assumed to still hold after H-052–H-054's edits to `build_model.py` — spot-checked live: `grep -c "sys.exit\|SystemExit"` returns ≥1 for all seven pipeline scripts; `build_model.py`'s Check 1 `SystemExit(1)` gate specifically re-confirmed still present and correctly placed (before `wb.save()`) after this session's projection-layer work. **Also ran the full `refresh_all.py` pipeline live during this audit** (not just grepped) — completed cleanly, zero ledger drift. **(a)**, confirmed, not assumed.

### 2.9 `model/data/*.csv` schemas vs. the scripts that read them, not independently validated elsewhere

- `employee-role-map.csv` — already covered in 2.1/2.2: it's fully derived from `ROLE_MAP_ROWS`, and the one place this isn't clear is `PAYROLL-UPDATE.md`'s own wording.
- `service-name-map.csv`, `catalog-type-map.csv` — checked whether anything writes to these (nothing does; `parse_invoices.py` only reads them) and whether drift is caught (`parse_invoices.py`'s own fail-closed gates catch an unrecognized header or unclassified kind). **(a)**, no gap.
- `model/requirements.txt` vs. actually-imported packages — checked live (`python3 -c "import openpyxl, pdfplumber"` against the pinned versions): exact match, `openpyxl==3.1.5`, `pdfplumber==0.11.10`. **(b)**, accurate.
- `.gitignore` vs. `financial-model.xlsx` — confirmed the exclusion line still exists and matches the actual generated filename. **(b)**, accurate.

### 2.10 A bonus finding: `model/PROJECTION-PLAN.md` Section 5 vs. its own Section 6

Not one of the named example classes, but found by the same discipline this audit applies everywhere: `PROJECTION-PLAN.md` Section 6's Decision 11 entry was updated in H-053 to say **"RESOLVED... owner-confirmed"** (75.9%, not crew labor's own 92.8%). **Section 5, in the same document, was never updated** — it still shows the worked example computed at 92.8% (crew labor $743.45 × 1.928 = $1,433.37) and still says the growth rate is "not yet owner-confirmed," and its summary table still says the High scenario "Reaches $6,000 in June 2027" — all superseded by H-053's actual result (75.9%, buffer reached May 2027, both Xavier's and the owner's payout trigger). **This has no effect on the actual model** (`build_model.py`/`financial-model.xlsx` already correctly use 75.9%, verified in H-053) — it's a planning-document-internal inconsistency, not a live bug. **(d)**.

---

## 3. Findings requiring a fix — proposed remediation and size (Step 4)

| # | Finding | Class | Fix | Size |
|---|---|---|---|---|
| 1 | `strategy/strategic-plan.md` line 141 still says "$25/hr base from day one" (Konji), contradicting `CONTEXT.md` D4's H-048 correction | (d) | Apply the same strikethrough + correction note `CONTEXT.md` D4 already carries, citing H-048, to this line | **Cheap** — one paragraph edit, no code |
| 2 | `PAYROLL-UPDATE.md` step 5 tells the reader to add a new employee to the CSV, which gets silently overwritten | (d) | Reword step 5 to say "add them to `ROLE_MAP_ROWS` in `model/populate_labor_from_payroll.py` (not the CSV directly — it's fully regenerated from that list every run)" | **Cheap** — one sentence |
| 3 | `CATALOG-UPDATE.md` step 7 doesn't mention `build_ledger_revenue.py` | (d) | Add the same step `REVENUE-UPDATE.md` already has (step 6 there), adapted for the catalog-refresh context | **Cheap** — copy an already-written paragraph, adjust wording |
| 4 | `PROJECTION-PLAN.md` Section 5 shows pre-Decision-11 (92.8%) figures and "not yet owner-confirmed," superseded by Section 6/H-053 | (d) | Update Section 5's worked numbers to the resolved 75.9%-based figures (already computed and verified in H-053 — no new computation needed, just transcription) | **Cheap** — numbers already exist in H-053's `HISTORY.md` entry, just need copying in |
| 5 | `RUNBOOK.md` Phase 7's "Done when" parenthetical says "this pass" ambiguously, citing only H-046–H-049 | (d), cosmetic | Reword to name the actual date/H-range or drop "this pass" | **Cheap, low priority** — cosmetic only, no reader is actually misled about a fact |

**No (c) undocumented-gap findings were found in this pass** — every dependency this audit checked already has either an automated safeguard or a written procedure; the problems found are all in the procedures' *accuracy* (class d), not their *existence*. This is a materially better result than H-051's original finding, which was a true (c) — no safeguard and no documentation at all.

---

## 4. Open decisions requiring sign-off (Step 5)

1. **Which of the five (d) findings should be fixed now, in a follow-on pass, vs. deferred?** *Recommendation:* fix all five now — every one is cheap (text-only edits, no new tooling, no design decisions), and #1/#2 in particular are worth closing before they cause real confusion (a future payroll refresh literally following #2's wording would recreate a mini version of H-051's own gap).
2. **Do any of these warrant a new automated fail-closed check, rather than just a documentation fix?** *Recommendation:* no, not for #1/#3/#4/#5 — they're all one-way prose/doc facts with no obvious mechanical invariant to check. #2 is more interesting: a script could in principle warn if `employee-role-map.csv` on disk differs from what `write_role_map()` is about to write (i.e., detect a hand-edit about to be clobbered) — but this is meaningfully more work than a doc fix, and the underlying risk (someone hand-editing a generated file) is already an unusual thing to do given every other generated ledger file in this repo follows the same overwrite convention. Flagged as a possible future enhancement, not recommended for this pass.
3. **Does anything in this audit rise to "another live bug, like H-051's" — a wrong number in the current, real output — warranting attention regardless of sequencing?** *No.* This is worth stating plainly: every finding here is either (a) a documentation-only drift with zero effect on any currently-generated number (`strategy/strategic-plan.md`'s stale line, `PROJECTION-PLAN.md` Section 5, `RUNBOOK.md`'s phrasing), or (b) a **latent** gap that would only cause a problem on a *future* refresh that hasn't happened yet (`PAYROLL-UPDATE.md`'s wrong instruction, `CATALOG-UPDATE.md`'s missing step) — not a wrong number sitting in `financial-model.xlsx` or any ledger CSV today. This is a materially different, less urgent situation than H-051's, where a routine refresh genuinely would have silently corrupted the ledger. Recommend treating these as important-but-not-urgent: worth fixing in the next available small pass, not an interrupt-everything fix.
4. **Should this audit be repeated periodically (e.g., at Revision Points, alongside the catalog-refresh cadence), or was this a one-time catch-up now that the pipeline has matured?** *Recommendation:* not decided here — flagged for the owner's judgment. The pattern this audit found (documents and CSVs correctly built at the time they were written, then drifting silently as a *later* change corrected one copy of a fact but not its duplicate) is structural to having any duplicated information at all, and will very likely recur as the projection layer, `strategy/`, and `CONTEXT.md` keep evolving together.

---

## 5. Addendum — 2026-07-12 (ad hoc, cataloged ahead of RP1, not a new full audit pass)

Logged during the Stripe balance-history retrospective (H-061 through H-064) so RP1's audit doesn't have to rediscover these from scratch. This is a targeted addition to this document, not a repeat of Steps 1–5 above.

**2.2's read/write-contract table is now stale for one row.** `match_payments.py`'s "Reads" column (line 43 of this document) listed only `reference/Relay*.csv, revenue-invoices.csv` — as of H-062, it also reads `reference/stripe-balance-history-*.csv` (via `load_stripe_fee_lookup()`), used as the ground-truth source for Stripe fee amounts on any payout it covers, with the pre-existing 3.9%+$0.30 formula kept as a fallback for payouts it doesn't. **This is also a genuinely different case from every other row in that table's last column:** every other script's output is protected by a fail-closed gate ("No" — an enforced check exists); this one is not, by design (`reference/STRIPE-UPDATE.md`'s "No fail-closed gate (deliberate)" section) — a stale or missing Stripe export doesn't fail the pipeline, it silently degrades fee precision for uncovered payouts. RP1 should update the table row itself when it next does a full pass; recorded here so the gap is known in the interim.

**2.7's Follow-Up-status spot-check is now stale for two items, expected given the dates.** That section (from the original H-055 pass, 2026-07-10) recorded #17 and #18 as still open/BLOCKED. Both are now resolved (#18 by H-062, #17 by H-063) — not a finding of drift, since the spot-check accurately reflected state as of its own date; flagged only so RP1 doesn't need to re-verify what's already been closed with a full paper trail (`CONTEXT.md` Follow-Up #17/#18 text, `HISTORY.md` H-061–H-064).

**New dependency chain to fold into RP1's own Section 2.2 pass:** `reference/stripe-balance-history-*.csv` → `model/match_payments.py` (`load_stripe_fee_lookup()`) → `model/data/ledger-overhead.csv`'s Stripe fee rows + (not yet, but possible per `CONTEXT.md` Follow-Up #25) `model/data/ledger-revenue.csv`'s aggregated payment rows. `reference/STRIPE-UPDATE.md` (new, H-064) now documents the refresh procedure and its deliberately-gate-free design, mirroring the other three `*-UPDATE.md` procedures this section already audits.
