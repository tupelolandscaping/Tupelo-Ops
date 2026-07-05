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
