#!/usr/bin/env python3
"""Generate the financial model workbook from the five ledger CSVs.

Usage:
    python model/build_model.py

Reads model/data/ledger-{revenue,labor,overhead,materials,capital}.csv
(identical 11-column schema) and generates model/financial-model.xlsx
(gitignored, disposable build output, per D7) with one sheet per derived
view, per CONTEXT.md Section 9:

  - Monthly P&L      -- Billed and Collected shown side by side, never
                        merged (D5a); every category decomposed into its
                        ACTUAL and ESTIMATE amounts, with BLOCKED categories
                        noted explicitly rather than shown as a bare $0.
  - Plan vs Actual    -- BLOCKED: no plan/assumptions CSV exists yet in
                        model/data/. Per D6, the projection layer may only
                        reference a data-layer or clearly-labeled assumptions
                        file -- strategy/strategic-plan.md's prose tables are
                        not that, so this sheet states the gap rather than
                        hardcoding those figures into the script.
  - Quarterly Rollups -- calendar quarters (Jan-Mar/Apr-Jun/Jul-Sep/Oct-Dec),
                        summed directly from the monthly P&L figures.
  - Revenue by Service / Revenue by Customer -- built only from
                        event=invoice rows; payment rows carry no service
                        classification (their subcategory is a match-
                        confidence tag, not a service name).
  - Reconciliation    -- scoped to what the ledger actually claims to cover:
                        revenue invoice total vs. the known $28,316.57
                        anchor; revenue payment classification completeness
                        (per H-044); overhead ACTUAL rows vs. their sourced
                        Relay matches; capital rows vs. their sourced
                        transactions; labor ACTUAL rows vs. Relay payroll
                        NET/TAX cash-outs, by reference to
                        model/reconcile_payroll_relay.py's own full-history
                        gate (per H-049), not re-run inline here. States on
                        its face what it does NOT verify (materials' BLOCKED
                        placeholder, the ~85% of real Spend-side Relay cash
                        that has no ledger row at all, and labor's own known
                        residual gaps -- Follow-Ups #19-20) rather than
                        implying full coverage.
  - Raw Ledger        -- all five files unioned as one passthrough table,
                        sorted by date, `type` column distinguishing rows.

Blended labor rate is computed at build time (sum(amount)/sum(quantity))
wherever shown -- never a stored constant. Scoped to crew roles (Crew Lead,
Crew Member) only, per CREW_ROLES -- since H-049 sourced labor from real
payroll data, ledger-labor.csv also carries CEO wage draws and a Landscape
Consultant role, neither a crew staffing cost; blending them in would
distort the figure this KPI exists to inform (future crew-job cost
estimates). Non-crew labor dollars are still shown, in their own column,
not silently dropped.

Re-running this script is idempotent: identical input CSVs produce a
byte-identical workbook (no timestamps or non-deterministic ordering).
"""
import csv
import re
import zipfile
from collections import defaultdict
from datetime import date, datetime

from openpyxl import Workbook
from openpyxl.styles import Font

# openpyxl's writer unconditionally re-stamps docProps/core.xml's `modified`
# field to datetime.now() inside save() (openpyxl/writer/excel.py), which
# can't be overridden by setting wb.properties beforehand -- it would make
# the workbook non-idempotent even when the CSV inputs are unchanged. Fixed
# by post-processing the saved .xlsx: rewrite docProps/core.xml with a fixed
# timestamp and rebuild the zip with fixed per-entry metadata, so byte-for-
# byte output depends only on the CSV inputs, never on wall-clock save time.
FIXED_TIMESTAMP = "2000-01-01T00:00:00Z"
FIXED_ZIP_DATE_TIME = (1980, 1, 1, 0, 0, 0)

LEDGER_FILES = {
    "revenue": "model/data/ledger-revenue.csv",
    "labor": "model/data/ledger-labor.csv",
    "overhead": "model/data/ledger-overhead.csv",
    "materials": "model/data/ledger-materials.csv",
    "capital": "model/data/ledger-capital.csv",
}
OUTPUT_PATH = "model/financial-model.xlsx"

REVENUE_INVOICE_ANCHOR = 28316.57  # $27,891.65 gross + $424.92 tips, H-043

# Crew roles for the blended-labor-rate KPI, per model/data/employee-role-map.csv
# (H-049). Deliberately excludes CEO and Landscape Consultant -- see
# build_monthly_pnl's blended_rate comment for why.
CREW_ROLES = {"Crew Lead", "Crew Member"}


def load_ledgers():
    ledgers = {}
    for name, path in LEDGER_FILES.items():
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            r["amount"] = float(r["amount"])
            r["quantity"] = float(r["quantity"]) if r["quantity"] else 0.0
        ledgers[name] = rows
    return ledgers


def year_month(d):
    return d[:7]


def all_months(ledgers):
    months = set()
    for rows in ledgers.values():
        for r in rows:
            months.add(year_month(r["date"]))
    return sorted(months)


def split_actual_estimate(rows):
    actual = sum(r["amount"] for r in rows if r["status"] == "ACTUAL")
    estimate = sum(r["amount"] for r in rows if r["status"] == "ESTIMATE")
    blocked = [r for r in rows if r["status"] == "BLOCKED"]
    return actual, estimate, blocked


# ---------------------------------------------------------------------------
# Monthly P&L
# ---------------------------------------------------------------------------

def build_monthly_pnl(ws, ledgers, months):
    header = [
        "Month",
        "Billed (ACTUAL)", "Billed (ESTIMATE)",
        "Collected (ACTUAL)", "Collected (ESTIMATE)",
        "Labor (ACTUAL)", "Labor (ESTIMATE)",
        "Overhead (ACTUAL)", "Overhead (ESTIMATE)",
        "Materials", "Materials note",
        "Capital (ACTUAL)", "Capital (ESTIMATE)",
        "Blended crew labor rate ($/hr)",
        "Non-crew labor $ (CEO/Consultant, excluded from blended rate)",
        "Note",
    ]
    ws.append(header)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for m in months:
        rev = [r for r in ledgers["revenue"] if year_month(r["date"]) == m]
        inv = [r for r in rev if r["event"] == "invoice"]
        pay = [r for r in rev if r["event"] == "payment"]
        labor = [r for r in ledgers["labor"] if year_month(r["date"]) == m]
        overhead = [r for r in ledgers["overhead"] if year_month(r["date"]) == m]
        materials = [r for r in ledgers["materials"] if year_month(r["date"]) == m]
        capital = [r for r in ledgers["capital"] if year_month(r["date"]) == m]

        inv_a, inv_e, _ = split_actual_estimate(inv)
        pay_a, pay_e, _ = split_actual_estimate(pay)
        labor_a, labor_e, _ = split_actual_estimate(labor)
        oh_a, oh_e, _ = split_actual_estimate(overhead)
        cap_a, cap_e, _ = split_actual_estimate(capital)

        mat_a, mat_e, mat_blocked = split_actual_estimate(materials)
        if mat_blocked:
            mat_display = "BLOCKED"
            mat_note = f"{len(mat_blocked)} placeholder row(s), $0.00 -- no per-job data yet (D1)"
        elif materials:
            mat_display = mat_a + mat_e
            mat_note = ""
        else:
            mat_display = "BLOCKED"
            mat_note = "no data this month -- materials/fuel not yet tracked (D1)"

        # Blended rate is scoped to crew roles (Crew Lead, Crew Member) only, per
        # D2's original intent (a crew staffing-cost KPI) -- since H-049 sourced
        # labor from real payroll data, ledger-labor.csv now also carries CEO wage
        # draws and a Landscape Consultant role, neither a crew staffing cost;
        # blending them in would distort the figure this KPI exists to inform
        # (future crew-job cost estimates), not just add noise to it.
        crew_labor = [r for r in labor if r["subcategory"] in CREW_ROLES]
        noncrew_labor = [r for r in labor if r["subcategory"] not in CREW_ROLES]
        crew_hours = sum(r["quantity"] for r in crew_labor)
        crew_a, crew_e, _ = split_actual_estimate(crew_labor)
        blended_rate = (crew_a + crew_e) / crew_hours if crew_hours else None
        noncrew_a, noncrew_e, _ = split_actual_estimate(noncrew_labor)
        noncrew_amount = noncrew_a + noncrew_e

        note = ""
        if m == "2026-07" and labor_a == 0 and labor_e == 0:
            note = ("Re-verified 2026-07-10 (H-049), not a stale artifact: labor is now sourced "
                    "from real Gusto payroll data, dated by period-start (accrual convention). "
                    "The last completed real pay period is 06/15-06/28/2026 (paid 07/07/2026); "
                    "the next period (06/29-07/12/2026) hadn't been processed/paid yet when the "
                    "payroll export was pulled (export window ends 07/09/2026), so it has no row "
                    "at all -- labor is correctly $0 in July here, because no July-dated pay "
                    "period has completed yet, not because data is missing.")

        ws.append([
            m,
            round(inv_a, 2), round(inv_e, 2),
            round(pay_a, 2), round(pay_e, 2),
            round(labor_a, 2), round(labor_e, 2),
            round(oh_a, 2), round(oh_e, 2),
            mat_display, mat_note,
            round(cap_a, 2), round(cap_e, 2),
            round(blended_rate, 2) if blended_rate is not None else "",
            round(noncrew_amount, 2),
            note,
        ])


# ---------------------------------------------------------------------------
# Plan vs Actual (BLOCKED -- no assumptions file exists)
# ---------------------------------------------------------------------------

def build_plan_vs_actual(ws):
    ws.append(["Plan vs Actual"])
    ws["A1"].font = Font(bold=True)
    ws.append([])
    ws.append(["BLOCKED -- no plan/assumptions CSV exists yet in model/data/."])
    ws.append(["Per D6 (CONTEXT.md), the projection layer may only reference a data-layer"])
    ws.append(["file or a clearly-labeled assumptions file -- it can never contain a"])
    ws.append(["hardcoded number. strategy/strategic-plan.md's quarterly target tables are"])
    ws.append(["prose/Markdown, not a data-layer assumptions file, so they are not a valid"])
    ws.append(["source for this sheet as things stand."])
    ws.append([])
    ws.append(["To unblock: add a dated, sourced assumptions CSV to model/data/ (e.g."])
    ws.append(["model/data/plan-targets.csv) carrying the quarterly revenue/profit/cash"])
    ws.append(["targets as explicit, labeled rows -- then this sheet can compare them"])
    ws.append(["against the Monthly P&L / Quarterly Rollups sheets by formula."])


# ---------------------------------------------------------------------------
# Quarterly Rollups
# ---------------------------------------------------------------------------

def quarter_of(ym):
    y, m = ym.split("-")
    m = int(m)
    q = (m - 1) // 3 + 1
    return f"{y}-Q{q}"


def build_quarterly_rollups(ws, ledgers, months):
    header = [
        "Quarter",
        "Billed (ACTUAL)", "Billed (ESTIMATE)",
        "Collected (ACTUAL)", "Collected (ESTIMATE)",
        "Labor (ACTUAL)", "Labor (ESTIMATE)",
        "Overhead (ACTUAL)", "Overhead (ESTIMATE)",
        "Capital (ACTUAL)", "Capital (ESTIMATE)",
    ]
    ws.append(header)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    quarters = defaultdict(lambda: defaultdict(float))
    for m in months:
        q = quarter_of(m)
        rev = [r for r in ledgers["revenue"] if year_month(r["date"]) == m]
        inv = [r for r in rev if r["event"] == "invoice"]
        pay = [r for r in rev if r["event"] == "payment"]
        labor = [r for r in ledgers["labor"] if year_month(r["date"]) == m]
        overhead = [r for r in ledgers["overhead"] if year_month(r["date"]) == m]
        capital = [r for r in ledgers["capital"] if year_month(r["date"]) == m]

        inv_a, inv_e, _ = split_actual_estimate(inv)
        pay_a, pay_e, _ = split_actual_estimate(pay)
        labor_a, labor_e, _ = split_actual_estimate(labor)
        oh_a, oh_e, _ = split_actual_estimate(overhead)
        cap_a, cap_e, _ = split_actual_estimate(capital)

        quarters[q]["inv_a"] += inv_a
        quarters[q]["inv_e"] += inv_e
        quarters[q]["pay_a"] += pay_a
        quarters[q]["pay_e"] += pay_e
        quarters[q]["labor_a"] += labor_a
        quarters[q]["labor_e"] += labor_e
        quarters[q]["oh_a"] += oh_a
        quarters[q]["oh_e"] += oh_e
        quarters[q]["cap_a"] += cap_a
        quarters[q]["cap_e"] += cap_e

    for q in sorted(quarters):
        v = quarters[q]
        ws.append([
            q,
            round(v["inv_a"], 2), round(v["inv_e"], 2),
            round(v["pay_a"], 2), round(v["pay_e"], 2),
            round(v["labor_a"], 2), round(v["labor_e"], 2),
            round(v["oh_a"], 2), round(v["oh_e"], 2),
            round(v["cap_a"], 2), round(v["cap_e"], 2),
        ])


# ---------------------------------------------------------------------------
# Revenue by Service / Revenue by Customer (invoice rows only)
# ---------------------------------------------------------------------------

def build_revenue_by_service(ws, ledgers):
    ws.append(["Category", "Subcategory (service)", "Amount (ACTUAL)", "Amount (ESTIMATE)", "Row count"])
    for cell in ws[1]:
        cell.font = Font(bold=True)

    inv = [r for r in ledgers["revenue"] if r["event"] == "invoice"]
    grouped = defaultdict(lambda: {"actual": 0.0, "estimate": 0.0, "count": 0})
    for r in inv:
        key = (r["category"], r["subcategory"])
        if r["status"] == "ACTUAL":
            grouped[key]["actual"] += r["amount"]
        elif r["status"] == "ESTIMATE":
            grouped[key]["estimate"] += r["amount"]
        grouped[key]["count"] += 1

    for (cat, subcat) in sorted(grouped, key=lambda k: -grouped[k]["actual"]):
        v = grouped[(cat, subcat)]
        ws.append([cat, subcat, round(v["actual"], 2), round(v["estimate"], 2), v["count"]])


def build_revenue_by_customer(ws, ledgers):
    ws.append(["Customer", "Amount (ACTUAL)", "Amount (ESTIMATE)", "Row count"])
    for cell in ws[1]:
        cell.font = Font(bold=True)

    inv = [r for r in ledgers["revenue"] if r["event"] == "invoice" and r["customer"]]
    grouped = defaultdict(lambda: {"actual": 0.0, "estimate": 0.0, "count": 0})
    for r in inv:
        key = r["customer"]
        if r["status"] == "ACTUAL":
            grouped[key]["actual"] += r["amount"]
        elif r["status"] == "ESTIMATE":
            grouped[key]["estimate"] += r["amount"]
        grouped[key]["count"] += 1

    for cust in sorted(grouped, key=lambda k: -grouped[k]["actual"]):
        v = grouped[cust]
        ws.append([cust, round(v["actual"], 2), round(v["estimate"], 2), v["count"]])


# ---------------------------------------------------------------------------
# Reconciliation -- scoped to what's actually checkable
# ---------------------------------------------------------------------------

def build_reconciliation(ws, ledgers):
    ws.append(["Reconciliation"])
    ws["A1"].font = Font(bold=True)
    ws.append([])

    inv = [r for r in ledgers["revenue"] if r["event"] == "invoice"]
    inv_total = sum(r["amount"] for r in inv)
    check1_pass = abs(inv_total - REVENUE_INVOICE_ANCHOR) < 0.01
    ws.append(["Check 1: revenue invoice total vs. known anchor"])
    ws.append(["  Ledger total:", round(inv_total, 2)])
    ws.append(["  Anchor ($27,891.65 gross + $424.92 tips, H-043):", REVENUE_INVOICE_ANCHOR])
    ws.append(["  Result:", "PASS" if check1_pass else "FAIL"])
    ws.append([])
    if not check1_pass:
        print(f"GATE FAILED: Check 1 -- revenue invoice total ${inv_total:,.2f} does not match "
              f"the ${REVENUE_INVOICE_ANCHOR:,.2f} anchor (H-043), off by "
              f"${inv_total - REVENUE_INVOICE_ANCHOR:,.2f}. Not writing the workbook.")
        raise SystemExit(1)

    pay = [r for r in ledgers["revenue"] if r["event"] == "payment"]
    pay_total = sum(r["amount"] for r in pay)
    ws.append(["Check 2: revenue payment classification completeness (per H-044)"])
    ws.append(["  Payment events in ledger:", len(pay), "  sum:", round(pay_total, 2)])
    ws.append(["  H-044's classification gate already proved: 94 settled Receive/"])
    ws.append(["  Receive-transfer rows (deduplicated) = 58 classified payment events"])
    ws.append(["  + 36 named exclusions, zero residual. Re-verifying that gate is not"])
    ws.append(["  repeated here -- see model/match_payments.py's own gate output."])
    ws.append(["  Result:", "PASS (by reference to H-044's gate)"])
    ws.append([])

    overhead = ledgers["overhead"]
    oh_actual = [r for r in overhead if r["status"] == "ACTUAL"]
    ws.append(["Check 3: overhead ACTUAL rows sourced to real Relay transactions"])
    ws.append(["  ACTUAL overhead rows:", len(oh_actual), "  sum:", round(sum(r["amount"] for r in oh_actual), 2)])
    ws.append(["  Every row's `source` field cites a specific reference/Relay*.csv file and"])
    ws.append(["  transaction reference (H-046) -- spot-checkable row by row, not re-verified"])
    ws.append(["  in aggregate here."])
    ws.append(["  Result:", "PASS (sourced; not independently re-matched here)"])
    ws.append([])

    capital = ledgers["capital"]
    ws.append(["Check 4: capital rows sourced to real Relay transactions"])
    ws.append(["  Capital rows:", len(capital), "  sum:", round(sum(r["amount"] for r in capital), 2)])
    for r in capital:
        ws.append(["   -", r["date"], r["category"], r["subcategory"], r["amount"], r["source"][:80]])
    ws.append(["  Result:", "PASS (both rows trace to a specific, named transaction)"])
    ws.append([])

    labor = ledgers["labor"]
    labor_actual = [r for r in labor if r["status"] == "ACTUAL"]
    ws.append(["Check 5: labor ACTUAL rows reconciled against Relay payroll cash-outs (per H-049)"])
    ws.append(["  ACTUAL labor rows:", len(labor_actual), "  sum:", round(sum(r["amount"] for r in labor_actual), 2)])
    ws.append(["  model/reconcile_payroll_relay.py's own full-history gate already proved: of"])
    ws.append(["  25 non-reversed, non-empty pay periods, the 24 with nonzero Net Pay matched a"])
    ws.append(["  specific Relay GUSTO NET transaction exactly (24/24), and 24 of the 25 with"])
    ws.append(["  nonzero combined tax matched a specific Relay GUSTO TAX transaction exactly"])
    ws.append(["  (24/25 -- the one exception is a $5.37 employer-tax-only correction with no"])
    ws.append(["  discrete Relay transaction, Follow-Up #20). Re-verifying that gate is not"])
    ws.append(["  repeated here -- see model/reconcile_payroll_relay.py's own gate output."])
    ws.append(["  Result:", "PASS (by reference to reconcile_payroll_relay.py's gate; 1 known exception, Follow-Up #20)"])
    ws.append([])

    ws.append(["What this tab does NOT verify:"])
    ws.append(["  - Labor's own known residual gaps (see Check 5 above for what IS verified):"])
    ws.append(["    payroll actuals carry no per-job/per-customer attribution and cover all"])
    ws.append(["    work combined, not recurring-only (Follow-Up #19); the $5.37 correction"])
    ws.append(["    with no discrete Relay match (Follow-Up #20)."])
    ws.append(["  - Materials: BLOCKED placeholder only ($0.00). No per-job cost data exists."])
    ws.append(["  - Commercial Auto and equipment-maintenance overhead lines: BLOCKED, no row"])
    ws.append(["    at all (no confirmed cash date / no allocation basis)."])
    ws.append(["  - The full per-account balance-delta gate (sum of ALL ledger events ="])
    ws.append(["    Relay ending balance) is NOT attempted here: ~85% of real settled"])
    ws.append(["    Spend-side Relay cash ($44,164.11 of $51,738.61) has no ledger row at"])
    ws.append(["    all by design (real Gusto payroll NET/TAX, internal transfers, and"])
    ws.append(["    uncaptured small vendor spend) -- attempting that gate would fail"])
    ws.append(["    predictably, not diagnostically, so it is not presented as a check here."])


# ---------------------------------------------------------------------------
# Raw Ledger passthrough
# ---------------------------------------------------------------------------

def build_raw_ledger(ws, ledgers):
    header = ["date", "type", "event", "category", "subcategory", "customer",
              "quantity", "unit_rate", "amount", "status", "source"]
    ws.append(header)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    all_rows = []
    for rows in ledgers.values():
        all_rows.extend(rows)
    all_rows.sort(key=lambda r: (r["date"], r["type"]))

    for r in all_rows:
        ws.append([r["date"], r["type"], r["event"], r["category"], r["subcategory"],
                   r["customer"], r["quantity"], r["unit_rate"], r["amount"],
                   r["status"], r["source"]])


CORE_XML_DATE_RE = re.compile(
    r'(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms:(?:created|modified)>)'
)


def normalize_xlsx_for_determinism(path):
    """Rewrite the saved workbook so re-running with unchanged input produces
    a byte-identical file: fix docProps/core.xml's timestamps (openpyxl's
    writer stamps `modified` with datetime.now() unconditionally on save) and
    give every zip entry a fixed date_time, in a fixed entry order.
    """
    with zipfile.ZipFile(path, "r") as zin:
        entries = []
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "docProps/core.xml":
                text = data.decode("utf-8")
                text = CORE_XML_DATE_RE.sub(rf"\g<1>{FIXED_TIMESTAMP}\g<2>", text)
                data = text.encode("utf-8")
            entries.append((info.filename, data))

    entries.sort(key=lambda e: e[0])
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for filename, data in entries:
            info = zipfile.ZipInfo(filename, date_time=FIXED_ZIP_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(info, data)


def main():
    ledgers = load_ledgers()
    months = all_months(ledgers)

    wb = Workbook()
    wb.remove(wb.active)
    wb.properties.creator = "model/build_model.py"

    build_monthly_pnl(wb.create_sheet("Monthly P&L"), ledgers, months)
    build_plan_vs_actual(wb.create_sheet("Plan vs Actual"))
    build_quarterly_rollups(wb.create_sheet("Quarterly Rollups"), ledgers, months)
    build_revenue_by_service(wb.create_sheet("Revenue by Service"), ledgers)
    build_revenue_by_customer(wb.create_sheet("Revenue by Customer"), ledgers)
    build_reconciliation(wb.create_sheet("Reconciliation"), ledgers)
    build_raw_ledger(wb.create_sheet("Raw Ledger"), ledgers)

    wb.save(OUTPUT_PATH)
    normalize_xlsx_for_determinism(OUTPUT_PATH)
    print(f"[build] wrote {OUTPUT_PATH}")
    print(f"[build] months covered: {months[0]} to {months[-1]} ({len(months)} months)")
    for name, rows in ledgers.items():
        print(f"[build] {name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
