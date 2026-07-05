# Tupelo-Ops

Business-operations and financial-model repository for Tupelo Landscaping LLC — strategic planning, biweekly check-ins, a from-scratch financial model built on an atomic ledger, and the raw source data everything reconciles against.

## Structure

```
strategy/     One-year strategic plan, operational toolkit, execution timeline.
check-ins/    Biweekly check-in template + dated check-in logs.
model/
  data/         Atomic ledger + assumption tables (CSV) — source of truth.
  build_model.py  Generates the workbook from data/ (created during the model build — Phase 7).
  requirements.txt  Pinned Python dependencies (e.g. openpyxl).
  financial-model.xlsx  Generated output — gitignored, regenerated on demand, never hand-edited (exists only after a build).
reference/    Raw source data (CRM exports, P&L, bank statements, overhead contracts) — ground truth, never edited.
.gitignore    Excludes the generated workbook and transient build artifacts.
```

The `model/` build files reflect the target structure — `build_model.py` and `financial-model.xlsx` are created later, in the model build (Phase 7), not present yet.

## Start here

- **`CONTEXT.md`** — full project background, locked decisions, and reasoning.
- **`CLAUDE.md`** — operating rules for Claude Code in this repository.
- **`SETUP.md`** — environment setup for a fresh Codespace.
- **`HISTORY.md`** — append-only audit log of decisions, milestones, and data changes.
