# HISTORY.md — Master Append-Only Audit Log

Single chronological record of what changed, when, and why, for Tupelo-Ops. Consolidates decisions, milestones, revisions, data changes, and tooling changes into one log — there is no separate `decisions/` file. Filtering to `Type: DECISION` yields the decision track alone. Per-file changelog tables embedded in individual documents are secondary convenience only; this log is canonical. Entries are append-only — never edit or delete a past entry; if a decision is later reversed, add a new entry that supersedes it and cite the superseded ID.

Dated entries are kept contiguous and chronological at the top. Undated entries follow, grouped by type; the foundational architecture/business decisions carried over from the pre-migration synthesis without an individually recorded date (D1–D10 and the cross-reference-check decision) are grouped in their own section at the end of the file, per `CLAUDE.md`'s history-logging convention.

---

### Dated entries

**H-001 · 2026-06-17 · MILESTONE**
The four core strategic artifacts — One-Year Strategic Plan, Operational Toolkit, Execution Timeline, and the (prior) Financial Model workbook — were reconciled to one another, closing the original nine-domain strategic analysis into a consistent set.
*Basis:* `CONTEXT.md` Section 2.

**H-002 · 2026-06 (late June 2026, exact date not recorded) · MILESTONE**
The weekday crew-lead hire (Konji) moved from "conversation underway" to fully finalized terms, ahead of the Execution Timeline's ~July 7, 2026 tripwire.
*Basis:* `CONTEXT.md` Section 2; terms detailed in D4.

**H-003 · 2026-07-01 · DATA**
Starting-cash anchor corrected from a $1,500 planning guess to $1,400, a confirmed operating-account bank reading as of 2026-07-01. Tagged interim ESTIMATE, not a firm anchor — superseded once Relay bank-statement consolidation (Follow-Up #9) establishes the full cash picture.
*Basis:* `CONTEXT.md` Section 3, Section 6 item D.

**H-004 · 2026-07-01 · DATA**
The stale Jan–Jun revenue validation figure (`Assumptions!B43 = $9,562.71`, captured 2026-06-17) was superseded by current exports through 2026-07-01 showing $12,726.01 billed / $10,973.57 collected, reconciled across the P&L, revenue-by-customer, and sales-tax reports. Carried gross-of-surcharge pending Follow-Up #10.
*Basis:* `CONTEXT.md` Section 3, Section 6 item F.

**H-005 · 2026-07-04 · DATA**
Fixed-overhead contract figures (insurance, workers' comp, commercial auto, payroll provider, CRM subscription) were sourced and recorded — owner-supplied. Added to `reference/` so overhead figures trace and can be reconciled per D8. The equipment-maintenance line remains BLOCKED pending a stated allocation base and method.
*Basis:* Owner-supplied directly in the 2026-07-04 working session, not derived from `CONTEXT.md` — `CONTEXT.md` predates this sourcing and only records the task as pending (Section 6 item I).

**H-006 · 2026-07-05 · MILESTONE**
Baseline import committed (`2fc197b`, "baseline import — unedited source files in repo homes"): 100 files renamed/relocated into their repo homes with zero content changes — 85 Relay bank-statement CSVs plus 15 other files (6 CRM CSV exports, the P&L PDF, the source `.xlsx` workbook, `fixed-overhead.md`, and the 4 strategy/check-in Markdown docs, plus `CONTEXT.md` and `RUNBOOK.md` at root). The `incoming/` staging folder was removed once empty.
*Basis:* `CONTEXT.md` Section 10 step 2; commit `2fc197b`.

**H-021 · 2026-07-05 · REVISION**
Reconciled `strategy/strategic-plan.md` to current ground truth: Konji's crew-lead compensation replaced the season-completion-bonus placeholder with his finalized terms ($25/hr base, 6% revenue share Sep '26–May '27, canvassing and winter project rates, phase-switch to a generic $25/hr line after May 2027), and the "weekday crew lead secured" checkbox was checked; the Xavier equipment-plan figure and Q1 milestone were corrected to ~$1,800, unpaid, demand-triggered in late winter (from the underspecified "~March" phrasing and the $1.5K equipment-plan placeholder); starting cash was corrected from the $1,500 planning guess to $1,400, tagged interim ESTIMATE pending Relay consolidation; the peak-revenue anchor was corrected from the normalized $4,500 to the actual May 2026 figure of $4,908, with the plan objective restated as ~$10,000 (from ~$9,000) and the quarterly target tables flagged as still derived from the superseded $4,500-anchor model, pending regeneration in the Phase 7 rebuild; and fixed monthly costs were updated from the ~$695 rough estimate to the sourced $696.58 itemized total (excluding equipment-maintenance, still BLOCKED).
*Basis:* `CONTEXT.md` Section 6 items C (crew-lead comp + checklist), D (Xavier terms + starting-cash anchor), and I (sourced overhead); the peak-anchor/objective correction follows the same actual-May-2026-figure logic as the Section 3 objective statement. *Closes:* Section 6 item C in full; the strategic-plan-facing portions of items D and I (the Assumptions Log rows); the plan-side half of the peak-anchor correction (the model-side regeneration remains open, pending Phase 7).

**H-022 · 2026-07-05 · REVISION**
Added an auto-insurance / Konji-insured-driver decision point to `strategy/execution-timeline.md`'s Oct 1–15 section, framing the before-vs-wait timing decision against the current 6-month term end (Oct 9, 2026).
*Basis:* `CONTEXT.md` Section 6 item J. *Closes:* the timeline-facing portion of item J (adding the dated decision point); the premium-increase figure itself remains BLOCKED pending an insurer quote.

**H-023 · 2026-07-05 · REVISION**
Reconciled the "Initiate now" checklist in `strategy/operational-toolkit.md`: the single stale item ("open the crew-lead conversation with Konji... begin sourcing a backup") was split into two, each carrying its true current status — the Konji conversation marked resolved (finalized terms, late June 2026), and backup weekday-lead sourcing marked active — consistent with the corrections already made to the execution timeline and strategic plan.
*Basis:* `CONTEXT.md` Section 6 item B (the same Konji-status reconciliation applied there).

**H-024 · 2026-07-05 · DATA**
The Jan–Jun 2026 revenue anchor was superseded: the stale model figure `Assumptions!B43` is replaced by the current exports, to be used when the model is rebuilt. The billed anchor and Konji's 6% base are carried gross-of-surcharge pending the tax session (#10).
*Basis:* `CONTEXT.md` Section 6 item F (the full instruction, figures, and surcharge caveat live there — this entry records the decision, not a duplicate of the numbers). *Status:* build-time instruction, open until the Phase 7 rebuild applies it and #10 resolves the surcharge composition.

**H-025 · 2026-07-05 · DATA**
The $5,000 "New Equipment" CRM entry (April 13) is recorded as a retroactive log of an already-owned asset (the existing F-150), not a new capital outflow — it must not be modeled as a future cash event in the rebuild.
*Basis:* `CONTEXT.md` Section 6 item H. *Status:* build-time instruction for Phase 7.

**H-026 · 2026-07-05 · DATA**
Relay account map confirmed (owner ground truth): 8735 Income, 3549 OpEx, 3550 Reserve, 8737 Taxes, 8736 Owner's Comp. The three non-operating accounts (3550, 8737, and 8736) verified $0 across all 17 months of statements; only 3549 (200 txns) and 8735 (49 txns) are active. Historical cash = Income + OpEx.
*Basis:* Owner confirmation + direct file check of `reference/` Relay CSVs.

**H-027 · 2026-07-05 · TOOLING**
Relay restructuring executed: Income→OpEx instant sweep active (Income max-balance $0 → 100% to OpEx); Owner's Comp (8736) deleted; Profit account renamed → Reserve (3550).
*Basis:* Owner actions in the Relay app, this session.

**H-028 · 2026-07-05 · DECISION**
Automated OpEx→Reserve ceiling deferred. Relay forbids an account being both source and destination in instant rules; near-zero value now (cash far below any ceiling); correct percentage-allocation design blocked on the model + Follow-Up #10. Ceiling value set at ~$8,000 for eventual use (basis: peak-season OpEx outflow $4,656.77 (May 2026 actual peak, from the header-correct 3549 parse) + $4,000 operating floor; revisit as revenue grows). Reserve funded manually in the interim. Post-model endpoint: a Profit First rule on Income (verified %s to OpEx/Reserve/Taxes), which preserves Income as a clean gross-revenue measurement point.
*Basis:* Design discussion, this session. *Status:* open, pending model + #10.

**H-029 · 2026-07-05 · DECISION**
Collapsing Income+OpEx into one account considered and deferred until the model exists; both accounts retained (Income's separation preserves a clean gross-revenue signal). Taxes (8737) allocation % remains BLOCKED pending #10.
*Basis:* Design discussion, this session.

**H-030 · 2026-07-06 · DATA**
Revenue ledger extracted from 68 source invoices and validated: line-item gross ties to invoice gross exactly ($27,891.65); Jan–Jul 2026 window ties to the Homeworks billed anchor to the penny ($12,726.01). Two parse defects found and corrected en route: a payment-stub-only page misread as a 69th invoice, and long descriptions wrapping the amount onto the wrong line (which had hidden $5,070.93).
*Basis:* Direct parse + three independent reconciliation checks against Homeworks exports.

**H-031 · 2026-07-06 · DATA**
Surcharge treatment resolved empirically. The ~6% is charged on top of each line's net price, but Homeworks' reported "billed revenue" is the gross figure — so the surcharge is embedded within the $12,726.01, not additional to it. Net service revenue Jan–Jul 2026 = $12,024.58; surcharge = $701.43. Note: this corrects an earlier statement in-session that the surcharge sat "on top of" the $12,726 anchor; the owner's understanding was correct and the earlier claim was wrong.
*Basis:* Per-invoice arithmetic across 68 invoices, cross-checked against the salestax export.

**H-032 · 2026-07-06 · DECISION**
Past revenue is tracked gross. Konji's 6% revenue share is computed on net service revenue (excluding the surcharge). The surcharge's structural treatment (retained revenue vs. pass-through liability) remains an open future decision (Follow-Up #10); if it changes, revisit this.
*Basis:* Owner decision, this session.

**H-033 · 2026-07-06 · MILESTONE**
Gate B (revenue mapping / flat export) substantially resolved; no longer blocks the model build. Residual: 40.7% bundled-line revenue is not service-resolvable historically (see #6, #13).
*Basis:* `reference/revenue-line-items.csv` and `reference/revenue-invoices.csv`, validated per H-030.

**H-034 · 2026-07-06 · REVISION**
Cross-reference reconciliation: Sections 6 (item E), 9 (revenue bullet), and 10 (step 5) of `CONTEXT.md` updated to reflect Gate B's resolution, so the document no longer describes Follow-Up #6 as a live blocker.
*Basis:* The CLAUDE.md cross-reference check, applied to the H-030–H-033 edits; the join drift was detected before commit. Note: this is the first autonomous catch by that rule since its adoption.

**H-035 · 2026-07-06 · TOOLING**
Revenue-ledger update standardized: `model/parse_invoices.py` with a fail-closed reconciliation gate (sum(line_gross) == sum(invoice gross); per-invoice tie-out; gross == net_subtotal + surcharge; no duplicate invoice numbers; optional `--expect-window` check against the Homeworks billed anchor); `reference/REVENUE-UPDATE.md` procedure; full-re-export-not-delta rationale (Homeworks records are mutable, so deltas would miss edits to prior invoices). The two revenue CSVs relocated from `reference/` to `model/data/` — they are script-regenerated derivatives, not immutable sources; `reference/` is now purely immutable raw sources. This supersedes the file paths cited in H-030 and H-033, which remain unedited and true as of their date.
*Basis:* Design discussion; script validated by byte-identical reproduction of the H-030 ledger's invoice-level file (`revenue-invoices.csv`).

**H-036 · 2026-07-06 · DATA**
Service classification corrected to use the invoice's literal service header. The prior ledger let free-text description lines override the header — an implementation artifact of the original parse, not a deliberate rule — which inconsistently reclassified some bundled lines into specific services (e.g., "General Maintenance" → "Mowing" when the description happened to start with a recognizable keyword, but not when it didn't) and understated the bundled-line share. Dollar amounts, dates, customers, and all invoice-level figures are unchanged; H-030's validation stands. 9 line items across 6 invoices changed classification (8 reclassified to "General Maintenance"/`is_bundle=TRUE`; 1 restored to its full literal header "Edging/Weed-whacking"). New bundled-line share: **56.6%** ($15,795.85 of $27,891.65), up from the prior 40.7% ($11,339.40). Supersedes the 40.7% figure cited in H-033 and in `CONTEXT.md` Follow-Up #6 / Section 9.
*Basis:* Owner review of the original parse logic; `model/parse_invoices.py` never scans description text for service names, only the invoice's literal service-header field.

**H-037 · 2026-07-06 · DATA**
Legacy service names mapped to the current catalog via `model/data/service-name-map.csv` (13 renames, owner-confirmed). Extraction verified the 27 distinct invoice headers are complete — the 48 headerless lines are description fragments, not service names. `service_raw` preserved alongside canonical `service`; a fail-closed gate now rejects unrecognized headers. No dollar amounts, dates, or customers changed. The three bundle labels (General Maintenance, Lawn Care, Lawn Maintenance) are not renames and remain unmapped; bundled share stays 56.6%.
*Basis:* Header extraction cross-checked against the 22-item Homeworks catalog; owner confirmed each mapping.

**H-038 · 2026-07-09 · DATA**
The current 22-item Homeworks catalog and its two Package definitions captured as dated reference snapshots (`reference/service-catalog-2026-07-09.csv`, verbatim from the Homeworks export including its trailing `null` row; `reference/service-packages-2026-07-09.csv`, transcribed from an owner screenshot). A currency mechanism was established so future catalog changes never require a code edit: an explicit "active snapshot" pointer line in `reference/README.md` (not glob-latest, since unlike invoices a newer catalog snapshot is not guaranteed to be a superset of an older one — an item could be renamed or discontinued), with the refresh procedure documented in `reference/CATALOG-UPDATE.md`. `model/parse_invoices.py` now reads valid catalog names from the pointed-to snapshot instead of the hardcoded `ALREADY_CANONICAL_SERVICES` set introduced in H-037. An item-vs-service axis was added via `model/data/catalog-type-map.csv` (`Bagged Mulch`, `Landscaping Blocks (stone)`, `New Plants` tagged `item`; the remaining 19 catalog rows tagged `service`) surfaced as a new `kind` column on every non-bundle line item in `model/data/revenue-line-items.csv`; bundle rows (`is_bundle=TRUE`) are left with `kind` blank, since a bundled visit mixes labor and possibly materials and can't be classified as one until Follow-Up #13 decomposes it. A new fail-closed gate rejects any mapped service name absent from `catalog-type-map.csv`, catching future catalog additions that aren't yet classified. Zero-revenue catalog items are now traceable to source rather than asserted: 7 of 22 have no billed line in the historical data — `Bagged Mulch`, `Landscaping Blocks (stone)`, `New Plants` (all 3 `item`-kind rows) and `Blowing`, `Material Pick-up`, `Seeding`, `Sod Placement` (4 of 19 `service`-kind rows). Homeworks' Packages feature (`General Maintenance`, `Lawn Care` package definitions) has never been used to bill an invoice — a distinct mechanism from the informal same-named bundle labels already in the ledger; the two must not be conflated (see `reference/CATALOG-UPDATE.md`). No dollar amounts, dates, or customers changed; `revenue-invoices.csv` remains byte-identical and `revenue-line-items.csv` changed only by the addition of the `kind` column.
*Basis:* Owner-supplied Homeworks "Items and Services" CSV export and "Packages" tab screenshot, both dated 2026-07-09; cross-checked programmatically against `model/data/service-name-map.csv` and `model/data/revenue-line-items.csv`.

**H-039 · 2026-07-06 · MILESTONE**
Gate A (bank consolidation) closed — the last pre-build gate. Four active-account Relay statements (3549, 8735, 3550, 8737) captured as dated reference sources (`reference/Relay (Partial) 2026-07-01 to 2026-07-06 #<NNNN>.csv`; the disambiguating end-date was added to the existing `Relay (Partial) YYYY-MM-DD #NNNN.csv` convention because the window-start label alone collides across multiple partial pulls within the same month — the pre-existing `2026-07-01` files are a distinct, earlier 7/3 pull and were not overwritten). Consolidated cash = **$1,225.33** as of 2026-07-06 (the latest transaction date found across the four files, not the `2026-07-01` filename label, which marks the window start) — independently computed from the statement files (`reference/cash-consolidated-2026-07-06.csv`), not asserted from the owner's figure alone: 3549 (OpEx) $1,225.33, 8735 (Income) $0.00 (instant-swept to OpEx per H-027), 3550 (Reserve) $0.00, 8737 (Taxes) $0.00. Reserve and Taxes confirmed still zero-activity — no statement for either account, across all 17+ prior months plus this window, has ever contained a transaction — consistent with H-026's "$0 across all 17 months" finding; their $0.00 status here is continuity, not a newly observed balance. This supersedes the $1,400 single-account interim estimate (H-003) as the cash anchor; full history ($1,500 planning guess → $1,400 interim → $1,225.33 verified) preserved in `strategy/strategic-plan.md` Section 9's Revision Note. Phase 7 (the model build) is now unblocked — both pre-build gates (B per H-033, A per this entry) are cleared.
*Basis:* Four owner-supplied Relay CSV exports dated 2026-07-09 (covering activity through 2026-07-06), independently reconciled: per-account ending balances and their sum computed directly from the files, matching the owner-stated $1,225.33 total exactly. One immaterial discrepancy noted: the 3549 file contains 11 transaction rows, not the 12 initially described — the dollar figure is unaffected.

---

### Undated revision

**H-019 · REVISION — Ledger schema: boolean `paid_flag` replaced by separate invoice/payment events.**
An earlier draft of the atomic ledger schema used a binary `paid_flag`. It was replaced by distinct invoice (billed) and payment (collected) event rows, because a boolean cannot represent partial payment and would overstate cash — the ~$1,752 billed/collected gap in current data is real. This redesign is folded into D5a (H-012).
*Basis:* `CONTEXT.md` Section 9, "Design note."

---

### Undated tooling

**H-020 · TOOLING — Repository hosted under a dedicated business GitHub account.**
`Tupelo-Ops` lives under a free GitHub account registered to the business email, not the owner's personal or work account, so the repository is a clean, portable business asset. In progress as of the GitHub transition.
*Basis:* `CONTEXT.md` Section 7 item 12(a); Section 10 step 1.

---

### Undated foundational decisions (recorded as of the pre-migration synthesis; exact session dates not specified in `CONTEXT.md`)

**H-007 · DECISION — D1: Materials/fuel explicit-zero placeholder.**
Model materials and fuel as explicit `$0` lines tagged BLOCKED rather than back-solving an estimate, because no per-job categorized data exists yet.
*Basis:* `CONTEXT.md` Section 4, D1.

**H-008 · DECISION — D2: Labor itemized by role, never blended.**
Assume 2 people per job (crew lead + crew member), 50/50 hours, at atomic rates ($25/hr lead, $20/hr member); ~20 person-hours per two-week period for recurring work, flagged ESTIMATE until time-tracking is live.
*Basis:* `CONTEXT.md` Section 4, D2.

**H-009 · DECISION — D3: Konji's revenue share is 6% of billed revenue.**
Konji leads essentially all work he is present for; his 6% share applies to billed (not collected) revenue on jobs he leads, beginning September 2026.
*Basis:* `CONTEXT.md` Section 4, D3.

**H-010 · DECISION — D4: Two-phase crew-lead cost structure.**
Konji's negotiated terms apply through May 2027; after that the crew-lead position reverts to a generic $25/hr line with no revenue share or bonuses, modeled as a phase switch.
*Basis:* `CONTEXT.md` Section 4, D4.

**H-011 · DECISION — D5: Atomic ledger + derived views.**
A single atomic actuals ledger is the source of truth; every summary (P&L, rollups, revenue by service/customer, blended labor rate) is derived from it by formula, never typed in — preventing the same fact from existing in multiple places and drifting.
*Basis:* `CONTEXT.md` Section 4, D5.

**H-012 · DECISION — D5a: Billing and payment are separate atomic events.**
An invoice (billed) and each payment against it (collected), including partial payments, are separate ledger events. Relay bank statements, not CRM payment records, are the source of truth for collected cash.
*Basis:* `CONTEXT.md` Section 4, D5a.

**H-013 · DECISION — D6: Data layer vs. projection layer, separated.**
The CSV data layer (actuals + flagged estimates) is physically separate from the forward projection layer, which may only reference derived data-layer values or labeled assumptions — never a hardcoded number.
*Basis:* `CONTEXT.md` Section 4, D6.

**H-014 · DECISION — D7: Generated-workbook build method.**
`build_model.py` reads plain-text CSV data and generates the Excel workbook as disposable output, enabling human-readable Git diffs and reproducible builds. The generated workbook is gitignored; dated snapshots are committed to `reference/` only at genuine milestones. Rejected alternative (hand-maintained single `.xlsx`) preserved the binary-diff problem this decision avoids.
*Basis:* `CONTEXT.md` Section 4, D7.

**H-015 · DECISION — D8: Self-reconciliation tab, honestly scoped.**
The generated workbook includes a tab verifying revenue and collected cash against CRM exports and Relay statements. It explicitly does not yet verify itemized fixed overhead or materials/fuel, for lack of underlying per-job/contract data.
*Basis:* `CONTEXT.md` Section 4, D8.

**H-016 · DECISION — D9: Tooling — lean now, heavyweight orchestration later.**
Use GitHub + Claude Code in VS Code via Codespaces, with a lean project-specific `CLAUDE.md`. Multi-agent orchestration (Ruflo/claude-flow) is deferred until a task justifies parallel agents; it serves only as a structural reference for what `CLAUDE.md` can contain.
*Basis:* `CONTEXT.md` Section 4, D9.

**H-017 · DECISION — D10: RAG readiness now, adoption on trigger.**
Keep the repository retrieval-ready through free structural conventions (plain text, clean sections, front-matter, atomic files). Adopt an actual vector database only when the corpus outgrows the context window or recurring semantic search becomes necessary; keep the eventual choice tool-agnostic rather than locking into RuVector early.
*Basis:* `CONTEXT.md` Section 4, D10.

**H-018 · DECISION — Cross-reference-legibility review check adopted.**
`CLAUDE.md` and future structured-document edits are governed by a triggered check: verify that a reader arriving at a changed section can reach any justification, dependency, or definition it relies on without already knowing where it lives.
*Basis:* three external review rounds of `CONTEXT.md` in which every surviving defect was cross-reference/join drift, not content error (`CONTEXT.md` Section 6 item G3).
