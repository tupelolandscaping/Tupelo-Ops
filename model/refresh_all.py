#!/usr/bin/env python3
"""Run the full data-refresh pipeline in the correct order (Process/tooling
reliability pass, H-051).

Usage:
    python model/refresh_all.py

Closes a real process gap found in the "what's left" review: refreshing the model's
data required manually remembering the correct order across six scripts, with no
single command and no written reference for what that order is. This script runs
each stage as a subprocess -- exactly equivalent to typing `python model/<script>.py`
by hand in sequence -- and halts immediately if any stage fails (every stage is now
fail-closed per this same pass's Step 2 hardening), printing a clear summary of what
ran and what didn't.

Pipeline order and why it's fixed:
  1. model/parse_invoices.py        -- Homeworks PDF -> revenue-invoices.csv /
                                        revenue-line-items.csv.
  2. model/build_ledger_revenue.py  -- those CSVs -> ledger-revenue.csv's
                                        invoice/surcharge/tip rows. Must run before
                                        step 3, which only appends payment rows on
                                        top and otherwise leaves the file alone.
  3. model/match_payments.py        -- Relay statements + revenue-invoices.csv ->
                                        ledger-revenue.csv's payment rows +
                                        ledger-overhead.csv's Stripe fee rows.
  4. model/populate_step4.py        -- Relay statements -> ledger-overhead.csv's
                                        remaining categories, ledger-materials.csv,
                                        ledger-capital.csv. Independent of steps 5-6
                                        (H-049/H-050 fixed the category-collision
                                        bug that used to make this order-sensitive).
  5. model/populate_labor_from_payroll.py -- Gusto payroll exports ->
                                        ledger-labor.csv + the employer-payroll-
                                        tax-burden rows in ledger-overhead.csv.
  6. model/reconcile_payroll_relay.py -- full-history gate: payroll totals vs.
                                        Relay GUSTO NET/TAX transactions.
  7. model/build_model.py           -- all five ledgers -> financial-model.xlsx
                                        (gitignored, regenerated, never committed).

Re-running this script is safe: every stage it calls is itself safe to re-run
(each rebuilds only the categories/rows it owns from source, per its own docstring).
"""
import subprocess
import sys

PIPELINE = [
    "model/parse_invoices.py",
    "model/build_ledger_revenue.py",
    "model/match_payments.py",
    "model/populate_step4.py",
    "model/populate_labor_from_payroll.py",
    "model/reconcile_payroll_relay.py",
    "model/build_model.py",
]


def main():
    # flush=True on every print here: without it, this process's own stdout
    # is fully buffered (not line-buffered) whenever stdout isn't a TTY (e.g.
    # piped or redirected to a file), so every banner below would sit unwritten
    # until this whole process exits -- appearing all at once, after every
    # child's own output, rather than interleaved with it as intended. Found
    # by testing: the first version of this script showed all child output
    # before any parent banner when its output was redirected to a file.
    ran = []
    for i, script in enumerate(PIPELINE):
        print(f"\n{'=' * 70}\n>>> [{i + 1}/{len(PIPELINE)}] {script}\n{'=' * 70}", flush=True)
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            not_run = PIPELINE[i + 1:]
            print(f"\n{'=' * 70}", flush=True)
            print(f"PIPELINE HALTED: {script} exited with code {result.returncode}.", flush=True)
            print(f"Completed: {', '.join(ran) if ran else '(none)'}", flush=True)
            print(f"Not run: {', '.join(not_run) if not_run else '(none)'}", flush=True)
            print(f"{'=' * 70}", flush=True)
            raise SystemExit(result.returncode)
        ran.append(script)

    print(f"\n{'=' * 70}", flush=True)
    print(f"PIPELINE COMPLETE -- all {len(PIPELINE)} stages ran successfully:", flush=True)
    for s in ran:
        print(f"  - {s}", flush=True)
    print(f"{'=' * 70}", flush=True)


if __name__ == "__main__":
    main()
