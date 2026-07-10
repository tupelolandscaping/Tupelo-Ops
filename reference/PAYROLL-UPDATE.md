# Payroll Ledger — Standing Update Procedure

## Why a full re-export and full re-run, never an incremental delta

Same reasoning as `REVENUE-UPDATE.md`: a fresh Gusto export is re-parsed from scratch into `model/data/ledger-labor.csv` (and the employer-payroll-tax-burden rows in `model/data/ledger-overhead.csv`) every time, rather than appending only the new pay periods. This is self-healing against any correction Gusto itself makes to a past period (e.g., the "Tax Reconciliation Payroll" true-up found in H-049) and costs nothing extra — the parse is a few seconds.

## Steps

1. Export a fresh Gusto **Payroll Journal Report** (per-employee, per-pay-period detail) covering the window needed. **Gusto only exports a rolling window (roughly one year) at a time**, so the current two files (`reference/README.md`'s "Payroll journal exports" section) will eventually age out on their older end and need a new export to keep coverage current — the same structural situation the Relay statements and the service catalog are already in.
2. Save it as `reference/tupelo-landscaping-llc-payroll-summary-<start>-to-<end>.csv`, dated by the coverage window, matching the existing files' naming convention. **Never overwrite a prior export** — each is its own immutable raw source (see `reference/README.md`).
3. Confirm the new export's window doesn't overlap or gap against the existing files' coverage, the same way the two current files were confirmed to cleanly abut with zero overlapping pay days (H-048). A gap or overlap changes how `model/populate_labor_from_payroll.py`'s `PAYROLL_GLOB` pattern will read the full history — check this before moving on.
4. Update `reference/README.md`'s "Payroll journal exports" section to list the new file alongside the existing ones.
5. Run:
   ```
   python model/populate_labor_from_payroll.py
   ```
   This fully rebuilds `model/data/ledger-labor.csv` from every payroll file matching the glob, and adds/replaces the `employer-payroll-tax-burden` rows in `model/data/ledger-overhead.csv`. **Watch the console output for an `[WARNING] ... employee(s) not found in role map` line.** If any appears, a new person is in the payroll data who isn't in `model/data/employee-role-map.csv` yet — add them (owner-confirmed job title, per the existing `employee,role,effective_date` schema; use a second dated row if their title has changed, the same way Xavier's Crew Lead → Crew Member change is recorded) and re-run. The loader hard-flags unlisted names rather than silently guessing a role.
6. Also watch for any newly discovered payday-block type. H-049 found one mid-build — an unmarked `"Tax Reconciliation Payroll"` block distinct from the marked `"Reversal Payroll"` blocks — that the parser needed explicit handling for. If a future export contains a structure the parser doesn't recognize, it will most likely surface as a `ValueError` or a name/value that looks wrong in the printed totals; don't silently work around it — extend the parser the same deliberate way, and document the new pattern in `HISTORY.md`.
7. Run:
   ```
   python model/reconcile_payroll_relay.py
   ```
   This is the full-history reconciliation gate (per H-049): every non-reversed, non-empty pay period's Net Pay and combined Employee+Employer Tax should match a specific Relay `GUSTO` `NET`/`TAX` transaction exactly. **Expect zero unexplained exceptions beyond the one already-known $5.37 Tax Reconciliation correction (Follow-Up #20).** If a *new* exception appears, stop — do not commit. Investigate it the same way the $5.37 gap was investigated (check neighboring periods for an absorbed adjustment, check Relay directly around the payday in question) before deciding how to record it; do not force a match or silently drop it.
8. Re-run `python model/populate_step4.py` only if overhead's other categories (Gusto fee, insurance, CRM, etc.) also need refreshing against newer Relay statements — it is order-independent with step 5 (H-049 fixed the category-collision bug that used to make this unsafe) and will not disturb the employer-payroll-tax-burden rows written in step 5.
9. Regenerate the workbook:
   ```
   python model/build_model.py
   ```
10. Review `git diff` on `model/data/employee-role-map.csv` and `model/data/ledger-labor.csv` (and `ledger-overhead.csv`'s new tax-burden rows) — this diff *is* the period's labor update: new pay periods, any roster change, any rate/title change.
11. Log the refresh in `HISTORY.md` (new export filed, any new employee or role change, the gate's exact result).
12. Commit.

## Cadence

Refresh whenever the current export's window is about to age out (Gusto's ~1-year rolling export), or immediately whenever the owner reports a new hire, a dismissal, or a rate/title change — the time-varying role-map design exists specifically so a mid-history change like Xavier's doesn't require restructuring the file, only adding a row.

## What a re-run produces and gates on

**Mirror-the-source row design (H-049).** One ledger row per (employee, pay period) the Gusto export actually lists, including genuine `$0`-hour rows for still-employed-but-idle people, and no row at all for periods before hire or after dismissal — a dismissed employee should simply stop appearing, never trailing off with `$0` rows.

**Reversal and correction handling.** Marked `"Reversal Payroll"` payday-blocks are skipped entirely (the clean resubmission payday is used instead); an unmarked `"Tax Reconciliation Payroll"` block (zero wages, employer-tax-only) gets no labor row but does contribute to the employer-payroll-tax-burden overhead total.

**Employer-payroll-tax-burden.** One aggregated row per pay period in `model/data/ledger-overhead.csv` (`category="Gusto", subcategory="employer-payroll-tax-burden"`), summing Employee Taxes + Employer Taxes across all employees that period — kept separate from `ledger-labor.csv` so labor's `amount` keeps meaning "wages paid to a person," not fully-loaded cost.

**Full-history reconciliation gate.** `model/reconcile_payroll_relay.py` is the standing hard gate for this ledger (per H-049): every non-reversed, non-empty pay period's Net Pay and combined tax must match a specific Relay transaction exactly. As of H-049, 24 of 24 periods with nonzero Net Pay matched, and 24 of 25 periods with nonzero combined tax matched — the one exception (Follow-Up #20) is a known, small ($5.37), immaterial gap, not a failure of the gate's design.

**Known, standing limitations (do not treat a refresh as resolving these).** Payroll actuals carry no per-job or per-customer attribution, and cover all hours combined (recurring + one-off project work), broader in scope than `CONTEXT.md` D2's original recurring-only estimate (Follow-Up #19). See `HISTORY.md` H-049 for the full record of the initial build.
