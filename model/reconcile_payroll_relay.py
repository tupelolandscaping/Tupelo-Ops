#!/usr/bin/env python3
"""Full-history reconciliation gate (Sequencing Step 5, Part 2, Step 5).

For every non-reversed payroll pay-period-block, confirm:
  - the source's own "Payroll Totals" Net Pay figure matches a specific
    Relay GUSTO Spend transaction with reference "NET <id> ..." exactly, and
  - the source's combined Employee Taxes + Employer Taxes total matches a
    specific Relay GUSTO Spend transaction with reference "TAX <id> ..."
    exactly.

Matches are by exact amount + payee, restricted to Relay rows not already
excluded as a bounced/reversed settlement (mp.exclude_reversed_spend), and
each Relay row is consumed at most once (no double-matching one Relay
transaction against two payroll periods).
"""
import sys
sys.path.insert(0, "model")
import match_payments as mp
from populate_labor_from_payroll import parse_payroll_file
import glob

PAYROLL_GLOB = "reference/tupelo-landscaping-llc-payroll-summary-*.csv"

# Already-known, documented, immaterial exceptions (Follow-Up #20: a $5.37
# VA Unemployment true-up with no discrete Relay transaction). Matched by
# stable substring, not full string, so wording tweaks elsewhere don't break
# this. Any exception NOT matching one of these is a genuine, new failure --
# see main()'s gate below.
KNOWN_EXCEPTIONS = [
    "tax-reconciliation, payday 03/31/2026",
]


def is_known_exception(msg):
    return any(k in msg for k in KNOWN_EXCEPTIONS)


def cents(x):
    return round(float(x) * 100)


def main():
    all_periods = []
    for fn in sorted(glob.glob(PAYROLL_GLOB)):
        periods = parse_payroll_file(fn)
        for p in periods:
            p["source_file"] = fn
        all_periods.extend(periods)
    kept_periods = [p for p in all_periods if not p["reversal"]]

    raw, deduped, dup = mp.load_relay_rows()
    spend = [r for r in deduped if r["txn_type"] == "Spend" and r["payee"] == "GUSTO"]
    kept_spend, excluded_spend = mp.exclude_reversed_spend(spend, deduped)

    net_pool = [r for r in kept_spend if r["reference"].startswith("NET")]
    tax_pool = [r for r in kept_spend if r["reference"].startswith("TAX")]
    used_net = set()
    used_tax = set()

    checked = 0
    net_matched = 0
    tax_matched = 0
    exceptions = []

    for p in kept_periods:
        n_emp = len([e for e in p["employees"] if e and e[0] not in ("Payroll Totals", "Totals")])
        if n_emp == 0:
            continue  # genuinely empty period, nothing to reconcile
        totals = p["totals"]
        header = p["header"]
        if not totals or len(totals) != len(header):
            exceptions.append(f"{p['period'] or p['payday']}: no usable Payroll Totals row")
            continue
        t = dict(zip(header, totals))
        net_pay = float(t.get("Net Pay", "") or 0)
        emp_tax = float(t.get("Employee Taxes", "") or 0)
        er_tax = float(t.get("Employer Taxes", "") or 0)
        total_tax = emp_tax + er_tax
        label = p["period"] or ("tax-reconciliation, payday " + p["payday"] if p["tax_reconciliation"]
                                 else "off-cycle, payday " + p["payday"])
        checked += 1

        if abs(net_pay) > 0.001:
            match = next((r for i, r in enumerate(net_pool)
                          if i not in used_net and cents(-r["amount"]) == cents(net_pay)), None)
            if match:
                used_net.add(net_pool.index(match))
                net_matched += 1
            else:
                exceptions.append(f"{label}: Net Pay ${net_pay:.2f} -- NO matching Relay NET txn found")
        if abs(total_tax) > 0.001:
            match = next((r for i, r in enumerate(tax_pool)
                          if i not in used_tax and cents(-r["amount"]) == cents(total_tax)), None)
            if match:
                used_tax.add(tax_pool.index(match))
                tax_matched += 1
            else:
                exceptions.append(f"{label}: combined tax ${total_tax:.2f} -- NO matching Relay TAX txn found")

    print(f"Periods checked (non-reversed, non-empty): {checked}")
    print(f"Net Pay exact matches: {net_matched}")
    print(f"Combined-tax exact matches: {tax_matched}")
    print(f"Relay NET-labeled Gusto txns available: {len(net_pool)} (used {len(used_net)})")
    print(f"Relay TAX-labeled Gusto txns available: {len(tax_pool)} (used {len(used_tax)})")
    print(f"Exceptions: {len(exceptions)}")
    for e in exceptions:
        tag = "(known, Follow-Up #20)" if is_known_exception(e) else "(NEW, unexpected)"
        print(f"  - {e}  {tag}")

    unexpected = [e for e in exceptions if not is_known_exception(e)]
    if unexpected:
        print(f"\nGATE FAILED: {len(unexpected)} exception(s) beyond the known, documented "
              f"$5.37 gap (Follow-Up #20). A new unreconciled period means either a data "
              f"problem or a genuine new gap that needs investigation -- see H-049's "
              f"reconciliation-gate design for how the known gap was investigated before "
              f"being accepted as immaterial. Do not force a match or silently accept this.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
