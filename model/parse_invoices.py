#!/usr/bin/env python3
"""Parse a Homeworks invoice-export PDF into the revenue ledger CSVs.

Usage:
    python model/parse_invoices.py [PDF_PATH] [--expect-window START END TOTAL]

If PDF_PATH is omitted, the newest reference/invoices_*.pdf (by filename) is used.
Overwrites model/data/revenue-invoices.csv and model/data/revenue-line-items.csv.
Exits nonzero if any reconciliation check fails; the CSVs are still written in
that case so the failure can be inspected, but should not be committed.

See reference/REVENUE-UPDATE.md for the standing update procedure.
"""
import argparse
import csv
import glob
import re
import sys
from datetime import datetime

import pdfplumber

BUNDLE_SERVICES = {"General Maintenance", "Lawn Care", "Lawn Maintenance"}
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_PREFIX_RE = re.compile(rf"^({MONTHS}) \d{{1,2}}, \d{{4}}\b")
AMOUNT_TAIL_RE = re.compile(r"(\d+\.\d{2})\s+([\d,]+\.\d{2})\s*$")
FOOTER_RE = re.compile(
    r"Subtotal\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s+"
    r"This Invoice\s+([\d,]+\.\d{2})\s+"
    r"Amount Paid\s+([\d,]+\.\d{2})\s+"
    r"Total Due\s+([\d,]+\.\d{2})",
    re.DOTALL,
)
CUSTOMER_ID_RE = re.compile(r"Customer #\s*(\d+)")
INVOICE_NUM_RE = re.compile(r"Invoice #\s*(\d+)")
INVOICE_DATE_RE = re.compile(r"Invoice Date(?:\s*/\s*Due Date)?\s+([A-Za-z]+ \d{1,2}, \d{4})")
CUSTOMER_NAME_RE = re.compile(r"(?m)^(.+?)\s+Outstanding Balance\s+[\d,]+\.\d{2}\s*$")
TIP_RE = re.compile(r"Tip Paid\s+([\d,]+\.\d{2})")

INVOICE_COLUMNS = [
    "invoice", "invoice_date", "customer_id", "customer", "net_subtotal",
    "surcharge", "gross", "amount_paid", "total_due", "tip", "status", "source",
]
LINE_ITEM_COLUMNS = [
    "invoice", "invoice_date", "service_date", "customer_id", "customer",
    "service", "is_bundle", "line_net", "surcharge_pct", "line_surcharge",
    "line_gross", "status", "source",
]

# Empirically measured from the PDF's word positions: lines that wrap within a
# single item are <=9.9pt apart vertically; the gap to the next item's first
# line is >=14.2pt. 12.0 sits cleanly between the two (validated against all
# 68 invoices in invoices_2025-06_2026-06.pdf). A page is an invoice only if
# it contains "Subtotal" -- a payment-stub-only page (an invoice's stub
# overflowing onto its own page) has no Subtotal and must not be misread as a
# separate invoice.
ITEM_GAP_THRESHOLD = 12.0


def parse_date(s):
    return datetime.strptime(s, "%B %d, %Y").strftime("%Y-%m-%d")


def cluster_rows(words, tol=2.0):
    """Group words into visual text rows by vertical position, preserving each
    row's top y-coordinate (needed for gap-based item segmentation)."""
    rows = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if rows and abs(w["top"] - rows[-1][0]) <= tol:
            rows[-1][1].append(w)
            rows[-1][0] = min(rows[-1][0], w["top"])
        else:
            rows.append([w["top"], [w]])
    return [(top, " ".join(w["text"] for w in sorted(ws, key=lambda w: w["x0"]))) for top, ws in rows]


def parse_page(page, page_index, source):
    text = page.extract_text() or ""
    if "Subtotal" not in text:
        return None  # payment-stub-only page, not an invoice

    top_text = text.split("PAYMENT STUB")[0]

    invoice_num = int(INVOICE_NUM_RE.search(top_text).group(1))
    customer_id = int(CUSTOMER_ID_RE.search(top_text).group(1))
    invoice_date = parse_date(INVOICE_DATE_RE.search(top_text).group(1))

    # Customer name is read from the payment stub's "Customer <Name>" line
    # (Homeworks' own labeled field), falling back to the header block only
    # when an invoice's stub overflows onto a separate page with no item list.
    customer = None
    if "PAYMENT STUB" in text:
        stub_text = text.split("PAYMENT STUB", 1)[1]
        cm = re.search(r"Customer\s+(.+)", stub_text)
        if cm:
            customer = cm.group(1).strip()
    if customer is None:
        customer = CUSTOMER_NAME_RE.search(top_text).group(1).strip()

    footer_m = FOOTER_RE.search(top_text)
    if not footer_m:
        raise RuntimeError(f"page {page_index}, invoice {invoice_num}: could not parse footer totals")
    net_subtotal, surcharge, gross, amount_paid, total_due = (
        float(g.replace(",", "")) for g in footer_m.groups()
    )
    tip_m = TIP_RE.search(top_text)
    tip = float(tip_m.group(1).replace(",", "")) if tip_m else 0.0

    words = page.extract_words()
    rows = cluster_rows(words)

    desc_top = next((t for t, txt in rows if txt.startswith("Description")), None)
    if desc_top is None:
        raise RuntimeError(f"page {page_index}, invoice {invoice_num}: no 'Description' row found")
    subtotal_top = next((t for t, txt in rows if txt.startswith("Subtotal") and t > desc_top), None)
    if subtotal_top is None:
        raise RuntimeError(f"page {page_index}, invoice {invoice_num}: no 'Subtotal' row found")

    region = [(t, txt) for t, txt in rows if desc_top < t < subtotal_top]
    region = [
        (t, txt) for t, txt in region
        if not (txt.startswith("Property Address:") or txt.startswith("Property Not Assigned"))
    ]

    blobs = []
    prev_top = None
    for t, txt in region:
        if prev_top is None or (t - prev_top) > ITEM_GAP_THRESHOLD:
            blobs.append([txt])
        else:
            blobs[-1].append(txt)
        prev_top = t

    line_items = []
    last_date = invoice_date
    for blob in blobs:
        header = blob[0]
        dm = DATE_PREFIX_RE.match(header)
        if dm:
            service_date = parse_date(dm.group(0))
            last_date = service_date
            rest_lines = [header[dm.end():].strip()] + blob[1:]
        else:
            # No leading date: inherit the most recently seen date within
            # this invoice (falls back to invoice_date if none seen yet).
            service_date = last_date
            rest_lines = list(blob)

        found = None
        service = None
        for i, line in enumerate(rest_lines):
            am = AMOUNT_TAIL_RE.search(line)
            if am:
                found = am
                # Service is always the literal header text -- Homeworks'
                # actual classification field -- never inferred from
                # free-text description content, even when the amount is
                # glued onto the header line itself.
                service = line[: am.start()].strip() if i == 0 else rest_lines[0].strip()
                break
        if found is None:
            raise RuntimeError(
                f"page {page_index}, invoice {invoice_num}: no amount found in item block {blob!r}"
            )

        pct = float(found.group(1))
        line_gross = float(found.group(2).replace(",", ""))
        line_net = round(line_gross / (1 + pct / 100), 2)
        line_surcharge = round(line_gross - line_net, 2)
        is_bundle = "TRUE" if service in BUNDLE_SERVICES else "FALSE"

        line_items.append({
            "invoice": invoice_num, "invoice_date": invoice_date, "service_date": service_date,
            "customer_id": customer_id, "customer": customer, "service": service,
            "is_bundle": is_bundle, "line_net": line_net, "surcharge_pct": pct,
            "line_surcharge": line_surcharge, "line_gross": line_gross,
            "status": "ACTUAL", "source": source,
        })

    invoice_row = {
        "invoice": invoice_num, "invoice_date": invoice_date, "customer_id": customer_id,
        "customer": customer, "net_subtotal": net_subtotal, "surcharge": surcharge,
        "gross": gross, "amount_paid": amount_paid, "total_due": total_due, "tip": tip,
        "status": "ACTUAL", "source": source,
    }
    return invoice_row, line_items


def parse_pdf(path):
    source = f"reference/{path.split('/')[-1]}"
    invoices, all_items = [], []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            result = parse_page(page, i, source)
            if result is None:
                continue
            inv, items = result
            invoices.append(inv)
            all_items.extend(items)
    invoices.sort(key=lambda r: (r["invoice_date"], r["invoice"]))
    all_items.sort(key=lambda r: (r["invoice_date"], r["invoice"]))
    return invoices, all_items


def reconcile(invoices, items, expect_window=None):
    failures = []

    total_line_gross = round(sum(r["line_gross"] for r in items), 2)
    total_invoice_gross = round(sum(r["gross"] for r in invoices), 2)
    if total_line_gross != total_invoice_gross:
        failures.append(
            f"sum(line_gross)={total_line_gross} != sum(invoice gross)={total_invoice_gross}"
        )

    items_by_invoice = {}
    for r in items:
        items_by_invoice.setdefault(r["invoice"], []).append(r)
    per_invoice_mismatches = []
    for inv in invoices:
        line_sum = round(sum(r["line_gross"] for r in items_by_invoice.get(inv["invoice"], [])), 2)
        if line_sum != round(inv["gross"], 2):
            per_invoice_mismatches.append((inv["invoice"], line_sum, inv["gross"]))
    if per_invoice_mismatches:
        failures.append(f"{len(per_invoice_mismatches)} invoice(s) where sum(line_gross) != gross: "
                         + ", ".join(f"#{n} (lines={ls} gross={g})" for n, ls, g in per_invoice_mismatches[:10]))

    gross_mismatches = []
    for inv in invoices:
        expected = round(inv["net_subtotal"] + inv["surcharge"], 2)
        if round(inv["gross"], 2) != expected:
            gross_mismatches.append((inv["invoice"], inv["gross"], expected))
    if gross_mismatches:
        failures.append(f"{len(gross_mismatches)} invoice(s) where gross != net_subtotal + surcharge: "
                         + ", ".join(f"#{n} (gross={g} expected={e})" for n, g, e in gross_mismatches[:10]))

    nums = [inv["invoice"] for inv in invoices]
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    if dupes:
        failures.append(f"duplicate invoice numbers: {dupes}")

    if expect_window is not None:
        start, end, expected_total = expect_window
        window_gross = round(
            sum(inv["gross"] for inv in invoices if start <= inv["invoice_date"] < end), 2
        )
        if window_gross != round(expected_total, 2):
            failures.append(
                f"window [{start}, {end}) gross={window_gross} != expected {expected_total}"
            )

    return failures


def write_csv(path, rows, columns):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def print_summary(invoices, items):
    total_gross = sum(r["gross"] for r in invoices)
    total_net = sum(r["net_subtotal"] for r in invoices)
    total_surcharge = sum(r["surcharge"] for r in invoices)
    bundle_gross = sum(r["line_gross"] for r in items if r["is_bundle"] == "TRUE")
    line_total_gross = sum(r["line_gross"] for r in items)
    bundle_pct = (bundle_gross / line_total_gross * 100) if line_total_gross else 0.0

    print()
    print("Summary")
    print("-------")
    print(f"  Invoices:            {len(invoices)}")
    print(f"  Line items:          {len(items)}")
    print(f"  Gross:               ${total_gross:,.2f}")
    print(f"  Net:                 ${total_net:,.2f}")
    print(f"  Surcharge:           ${total_surcharge:,.2f}")
    print(f"  Bundled-line share:  {bundle_pct:.1f}%  (${bundle_gross:,.2f} of ${line_total_gross:,.2f})")


def find_default_pdf():
    matches = sorted(glob.glob("reference/invoices_*.pdf"))
    if not matches:
        raise SystemExit("no reference/invoices_*.pdf found; pass a path explicitly")
    return matches[-1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path", nargs="?", default=None,
                         help="invoice-export PDF (default: newest reference/invoices_*.pdf)")
    parser.add_argument("--expect-window", nargs=3, metavar=("START", "END", "TOTAL"),
                         help="assert gross sum for invoice_date in [START, END) equals TOTAL")
    args = parser.parse_args()

    pdf_path = args.pdf_path or find_default_pdf()
    print(f"Parsing {pdf_path} ...")
    invoices, items = parse_pdf(pdf_path)

    expect_window = None
    if args.expect_window:
        start, end, total = args.expect_window
        expect_window = (start, end, float(total))

    failures = reconcile(invoices, items, expect_window)

    write_csv("model/data/revenue-invoices.csv", invoices, INVOICE_COLUMNS)
    write_csv("model/data/revenue-line-items.csv", items, LINE_ITEM_COLUMNS)

    print_summary(invoices, items)

    if failures:
        print()
        print("RECONCILIATION FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print()
    print("All reconciliation checks passed.")


if __name__ == "__main__":
    main()
