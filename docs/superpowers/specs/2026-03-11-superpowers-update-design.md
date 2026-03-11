# Superpowers Bundle Update Design

## Goal

Update `amplifier-bundle-superpowers` to adopt obra/superpowers' latest methodology learnings while preserving Amplifier's superior enforcement mechanisms, and fix two ecosystem-level issues discovered during investigation: staged sub-recipe composition in the recipe engine, and @-mention resolution in mode bodies.

## Background

This design is informed by two Parallax Discovery investigations totaling 30+ agent investigations across 5 waves:

**Investigation 1: obra/superpowers deep discovery** (3 waves, 17 agents) mapped the complete system — 14 skills, 5 platforms, prose-driven pipeline — and found 12 confirmed bugs/gaps. The key finding: anti-rationalization is the core architecture (~100+ entries, 3:1 ratio over process content).

**Investigation 2: Comparative alignment analysis** (2 waves, 17 agents) mapped mechanism-to-mechanism between both systems. It confirmed Amplifier's architecture is superior (modes, recipes, agents, tool blocking) and that obra's content has evolved significantly since the Amplifier bundle was based on it (~v4.3). This investigation also identified the recipe engine staged sub-recipe composition issue and the mode @-mention resolution issue.

All investigation artifacts are preserved in `.investigation/` and `.investigation-compare/` in the workspace.

## Approach

The guiding principle throughout: **use obra's skills as-is, only override when Amplifier-specific.** This means:

- Removing 5 of our 7 skills where obra's versions are equal or better
- Fixing the recipe engine to support composing staged sub-recipes (enabling recipe reuse without duplication)
- Fixing mode @-mention resolution so shared content can be referenced rather than duplicated
- Enriching mode, agent, and context files with obra's latest methodology learnings

Three repos are affected. Implementation order follows the dependency chain: recipe engine fix first, then mode @-mention fix, then superpowers bundle content updates.

## Architecture

### Repos Affected

| Repo | Changes | Scope |
|------|---------|-------|
| `amplifier-bundle-recipes` | Staged sub-recipe composition fix | ~140 lines new code + tests |
| `amplifier-bundle-modes` | @-mention resolution in mode bodies | Small engine change + tests |
| `amplifier-bundle-superpowers` | Skill strategy, recipe restructuring, mode enrichment, agent updates | Content changes + removed files + tests |

### Implementation Order

```
1. amplifier-bundle-recipes    (recipe engine fix — no dependencies)
         │
2. amplifier-bundle-modes      (mode @-mention fix — no dependency on 1, but must land before 3)
         │
3. amplifier-bundle-superpowers (content updates — depends on both 1 and 2)
```

## Components

### Section 1: Skill Strategy

**Principle:** Use obra's skills as-is. Only maintain our own when Amplifier-specific or when we need to override for correctness in the Amplifier environment.

**Changes to `amplifier-bundle-superpowers`:**

**Flip skill source order** in `behaviors/superpowers-methodology.yaml` — ours first (wins on collision), obra second. Currently obra is first; needs to be reversed because our skills exist specifically to override when needed.

**Remove 5 skills** that obra's versions are equal or better for (and with ours first in the ordering, we'd be incorrectly overriding obra's better versions):

| Skill to Remove | Reason |
|-----------------|--------|
| `systematic-debugging` | obra's is 2.7× larger with 10 companion files |
| `verification-before-completion` | obra's adds rationalization prevention table, regression test pattern |
| `finishing-a-development-branch` | obra's adds Common Mistakes, Red Flags, Integration sections |
| `code-review-reception` | obra's adds Real Examples, GitHub thread guidance |
| `dispatching-parallel-agents` | obra's adds DOT flowchart, real session example |

**Keep 2 Amplifier-specific skills:**

| Skill to Keep | Reason |
|---------------|--------|
| `integration-testing-discipline` | Amplifier-specific E2E discipline with container timing. No obra equivalent ever existed (verified via git history). |
| `superpowers-reference` | Reference tables for our modes, agents, recipes. No obra equivalent ever existed. Update content to reflect current state. |

**Git history verification:** Checked obra's full git history. No evidence that integration testing content or reference tables were ever present and removed. These topics are legitimately Amplifier-specific.

---

### Section 2: Recipe Engine Fix — Staged Sub-Recipe Composition

**Repo: `amplifier-bundle-recipes`**

**Problem:** When a `type: "recipe"` step calls a staged sub-recipe (one with approval gates), `ApprovalGatePausedError` propagates unhandled through the parent recipe, corrupting session state. This prevents composing independently-useful staged recipes into uber-recipes.

**Design:** Separate child sessions with parent backreference and approval forwarding. ~140 lines across 3 files. Zero schema changes. Zero breaking changes.

#### Mechanism

**1. `_execute_recipe_step()` (~15 lines):**
Before calling `execute_recipe()`, check if a child session was saved from a previous pause (stored as `_child_session_{step_id}` in context). If found, pass it as `session_id` to resume the child instead of creating a new one. Wrap the call in `try/except ApprovalGatePausedError` — on catch, save the child session reference in context and re-raise.

**2. Flat execution loop (`execute_recipe()` flat path, ~40 lines):**
Add `except ApprovalGatePausedError` alongside existing `except SkipRemainingError`. On catch: save parent state at current step (don't advance), mirror the child's approval on parent session via `set_pending_approval()`, save `pending_child_approval` metadata (child_session_id, child_stage_name, parent_step_id), then re-raise with parent's session_id.

**3. Staged execution loop (`_execute_staged_recipe()`, ~30 lines):**
Same pattern as flat loop but within stage step execution. Uses compound stage names (`"parent-stage/child-stage"`) for disambiguation.

**4. Approval forwarding (~50 lines):**
New `_forward_approval()` and `_forward_denial()` helper methods on the tool class in `__init__.py`. When the user approves the parent session's mirrored gate, these recursively forward the approval down to the child session (and any grandchild sessions for arbitrary nesting depth).

**5. Resume cascade:**
On resume, parent detects pending child approval was approved, clears the mirrored state, re-enters the recipe step. The step finds the saved child session_id in context, passes it to `execute_recipe()` which resumes the child. If the child hits another gate, the cycle repeats.

**6. Flat resume path (~10 lines):**
When resuming and pending approval exists, check approval status. If still PENDING, re-raise. If DENIED, raise error. If APPROVED, clear pending state, inject `_approval_message`, and continue.

**7. Validator warning (~5 lines):**
Warn on `parallel: true` foreach over recipe steps, since parallel approval gates are undefined behavior.

#### UX

User sees one session_id throughout. Approval prompts from child recipes surface through the parent with compound stage names. `_approval_message` flows to both child context (for its subsequent stages) and parent context (for downstream steps). User never needs to understand nesting.

#### Depth Handling

Each level saves its DIRECT child's session_id. Approval forwarding recurses. Resume cascades down naturally. Existing `max_depth=5` recursion limit bounds nesting. No artificial depth limit needed.

#### Edge Cases

| Scenario | Handling |
|----------|----------|
| Deep nesting (uber → child → grandchild) | Each level saves its direct child, forwarding recurses |
| Multiple gates in one child | Cycle repeats naturally, parent stays at the same step |
| Child completes, then parent's own gate fires | Different code path, no conflict |
| Denial cascades | Forwarded recursively via `_forward_denial()` |
| Flat child (no stages) | Never raises the error, zero impact |
| Cancellation during child execution | Already works via `parent_session_id` parameter |
| Orphan child sessions | Handled by existing `cleanup_old_sessions` (7-day TTL) |

---

### Section 3: Recipe Restructuring

**Repo: `amplifier-bundle-superpowers`**

**Problem:** The `superpowers-full-development-cycle.yaml` recipe's implementation stage uses a single implementer with self-review. The comment at line 268 says "three-agent pipeline per task" but the prompt says "self-review" — confirmed oversight (internal contradiction).

**Design:** With the recipe engine fix from Section 2 landing first, the full-development-cycle recipe can call the existing `subagent-driven-development.yaml` recipe directly as a `type: "recipe"` step. No extraction of a flat sub-recipe needed — the engine fix makes composition of staged recipes just work.

**Changes to `superpowers-full-development-cycle.yaml`, Stage 3 (Implementation):**

- Replace the current single-implementer-with-self-review step with a `type: "recipe"` step calling `subagent-driven-development.yaml`
- Pass `plan_path` from parent context
- The SDD recipe's internal `final-review` approval gate surfaces through the parent automatically
- After SDD completes, the parent's own Stage 3 approval gate fires

**No new recipe files needed.** The SDD recipe stays exactly as-is — independently useful AND composable.

**Context variable compatibility:** Verify during implementation that the SDD recipe's expected input variables (`plan_path`) align with what the full-cycle recipe produces. Adapt context mapping in the `type: "recipe"` step if needed.

---

### Section 4: Mode Content Enrichment

**Repos: `amplifier-bundle-modes` (engine fix) + `amplifier-bundle-superpowers` (content)**

#### 4a. Fix @-mention resolution in mode bodies

**Repo: `amplifier-bundle-modes`**

Currently, @-mentions in mode markdown bodies are injected as literal strings — the LLM sees `@superpowers:context/debugging-techniques.md` as text, not resolved content. This was confirmed by code-tracing the full injection path: `parse_mode_file()` reads raw text, `handle_provider_request()` interpolates verbatim into `<system-reminder>`, `HookResult.context_injection` is a plain string with no `load_mentions()` call anywhere.

In contrast, agent `.md` bodies DO resolve @-mentions via `load_mentions()` in `Bundle._create_system_prompt_factory()`.

**Fix:** Add `load_mentions()` processing to the hooks-mode `handle_provider_request()` path before building the system-reminder. This requires access to the `mention_resolver` capability (already available in the hooks-mode module for directory discovery). This is a small change but benefits the whole ecosystem — any bundle's modes can then reference context files via @-mentions.

**The existing `debug.md:210` @-mention (`@superpowers:context/debugging-techniques.md`) gets fixed for free** — it's been silently broken since creation.

#### 4b. Create shared cross-mode context file

**Repo: `amplifier-bundle-superpowers`**

Create `context/shared-anti-rationalization.md` (or similar) containing anti-rationalization content that applies across multiple workflow phases (e.g., "spirit vs letter" inoculation, YAGNI reminders, false-completion prevention). This file is @-mentioned from multiple modes, avoiding duplication now that @-mentions resolve.

#### 4c. Enrich 5 mode files with obra's latest guidance

**Repo: `amplifier-bundle-superpowers`**

| Mode File | Lines Added | Content |
|-----------|-------------|---------|
| `modes/brainstorm.md` | ~30 | Architecture guidance ("design for isolation, testability, minimal interfaces"), scope assessment (project-level evaluation before detailed design), user review gate after spec creation |
| `modes/debug.md` | ~35 | "If 3+ fixes failed: question the architecture" escalation, "Human Partner Signals You're Doing It Wrong" (5 redirections) |
| `modes/execute-plan.md` | ~25 | Implementer status protocol (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED), model selection guidance (cheap/standard/capable by task complexity) |
| `modes/verify.md` | ~10 | Regression test verification pattern (Red-Green regression cycle) |
| `modes/write-plan.md` | ~15 | File structure planning (explicit step for file decomposition before tasks) |

**Total:** ~115 lines of new content across 5 mode files, using @-mentions for shared content.

---

### Section 5: Agent & Context Updates

**Repo: `amplifier-bundle-superpowers`**

#### Agent Updates

**`agents/implementer.md` (~25 lines):**
- Add status protocol — DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED with guidance for each
- Add architecture guidance — design for isolation, prefer small files, minimize interfaces

**`agents/code-quality-reviewer.md` (~15 lines):**
- Add architecture-level checks — file decomposition review, size growth detection, coupling analysis
- YAGNI check at the review layer

**`agents/spec-reviewer.md` (~5 lines):**
- Strengthen institutional distrust framing from obra's latest phrasing

**`agents/brainstormer.md` and `agents/plan-writer.md`:**
- No changes needed — Amplifier-specific document creation agents

#### Context File Updates

**`context/instructions.md`:**
- Update `<STANDING-ORDER>` to reflect simplified skill strategy

**`context/philosophy.md`:**
- Add "spirit vs letter" inoculation if not already present (~5 lines)

**`context/tdd-depth.md` and `context/debugging-techniques.md`:**
- Verify these don't wastefully duplicate what obra's skills now provide. Intentional reinforcement for sub-agents (who don't see obra's skills) is fine; pure duplication is not.

**`behaviors/superpowers-methodology.yaml`:**
- Flip skill source order — ours first, obra second (the one-line change implementing Section 1)

**Total:** ~50 lines of new agent content, 1 line changed in behavior YAML.

## Data Flow

### Recipe Composition Flow (Section 2)

```
User starts full-development-cycle recipe
  → Parent recipe executes stages 1-2 normally
  → Stage 3: parent encounters type: "recipe" step for SDD
    → Engine creates child session for SDD recipe
    → SDD executes until it hits its "final-review" approval gate
    → ApprovalGatePausedError caught by parent
    → Parent mirrors approval gate with compound name "implementation/final-review"
    → User sees approval prompt, approves
    → Parent forwards approval to child session
    → Child resumes, completes
    → Parent continues to its own Stage 3 approval gate
  → Stages 4-5 execute normally
```

### Mode @-mention Resolution Flow (Section 4a)

```
Mode file loaded (e.g., debug.md)
  → parse_mode_file() reads raw markdown (unchanged)
  → handle_provider_request() builds system-reminder
  → NEW: load_mentions() scans for @namespace:path patterns
  → NEW: Each @-mention resolved to file content via mention_resolver
  → NEW: Resolved content injected inline (replacing the @-mention literal)
  → HookResult.context_injection contains fully-resolved content
  → LLM receives actual file content instead of literal @-mention strings
```

## Error Handling

### Recipe Engine (Section 2)

- **`ApprovalGatePausedError` in child:** Caught by parent's `_execute_recipe_step()`, child session saved, error re-raised with parent session_id
- **Denial forwarding:** Recursive — denial propagates from parent through all child/grandchild sessions
- **Orphan child sessions:** Cleaned up by existing `cleanup_old_sessions` (7-day TTL)
- **Max nesting depth exceeded:** Existing `max_depth=5` recursion limit prevents unbounded nesting
- **Parallel foreach + staged sub-recipe:** Validator emits a warning (parallel approval gates are undefined behavior)

### Mode @-mention Resolution (Section 4a)

- **Invalid @-mention path:** Graceful error — does not break mode injection. Mode still loads with remaining content.
- **Missing file:** Clear error message identifying the unresolvable @-mention
- **No @-mentions present:** Zero behavioral change — mode bodies without @-mentions work identically to before

## Testing Strategy

### `amplifier-bundle-recipes` (Recipe Engine Fix)

**Unit tests:**
- `_execute_recipe_step()` with staged sub-recipes — child session creation, `ApprovalGatePausedError` catch, parent state checkpoint, child session reference saved in context
- Approval forwarding — `_forward_approval()` recursion, denial forwarding, `_approval_message` propagation to both parent and child
- Resume cascade — parent resume triggers child resume, child completion returns to parent, multiple gates in one child cycle correctly

**Integration tests:**
- Flat parent → staged child → approval → resume → completion
- Staged parent → staged child → child gate → parent gate → completion
- 3-level nesting (uber → child → grandchild)

**Edge case tests:**
- Parallel foreach + staged sub-recipe → verify validator warning

### `amplifier-bundle-modes` (@-mention Resolution Fix)

**Unit tests:**
- Mode body with `@namespace:path` resolves to actual file content in injected system-reminder
- Mode body without @-mentions works unchanged
- Invalid @-mention path produces graceful error, doesn't break mode injection

**Integration tests:**
- A superpowers mode with `@superpowers:context/shared-file.md` actually injects the shared file content

### `amplifier-bundle-superpowers` (Content Updates + Restructuring)

- Update structural tests to reflect reduced skill count (7 → 2)
- Update tests to verify flipped skill source ordering
- Add test: full-development-cycle recipe's implementation stage uses `type: "recipe"` calling SDD
- Add test: no Claude Code contamination in new/modified content (`TodoWrite`, `CLAUDE.md`, `Skill tool`)
- Add test: mode files have expected new sections (architecture guidance in brainstorm, status protocol in execute-plan, etc.)
- Existing tests for mode transitions, tool wiring, pipeline ordering must still pass

## Open Questions

All design decisions were resolved during the brainstorm conversation:

| Question | Resolution |
|----------|------------|
| Anti-rationalization placement | Modes (Amplifier advantage — always in attention) |
| Recipe composition approach | Fix the engine properly, then compose staged recipes directly |
| Skill strategy | Use obra's as-is, override only when Amplifier-specific, flip source order |
| @-mention resolution | Fix it in the modes engine (benefits whole ecosystem) |
| Shared content across modes | Use @-mentioned context files (enabled by the modes fix) |
