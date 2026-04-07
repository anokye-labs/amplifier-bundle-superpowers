# Superpowers Behavioral Parity Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Close 7 behavioral gaps between amplifier-bundle-superpowers and upstream obra/superpowers by porting visual companion scripts, creating new agents/context/skills, restoring dropped content, and wiring everything together in the behavior YAML.

**Architecture:** Port proven scripts verbatim from obra, create Amplifier-native equivalents where adaptation is needed (code-reviewer agent, SDD walkthrough, visual companion guide), restore dropped content to existing files, and wire all new components through the behavior YAML and mode/agent @mentions.

**Tech Stack:** Markdown (modes, agents, context), YAML (behavior config), Node.js + Bash (visual companion scripts), HTML/CSS/JS (companion frame + helper)

---

## Phase 1: Core New Content

All tasks in this phase create new files. No dependencies between tasks — they can be implemented in any order.

---

### Task 1: Port Visual Companion Scripts

**Files:**
- Create: `scripts/server.cjs`
- Create: `scripts/start-server.sh`
- Create: `scripts/stop-server.sh`
- Create: `scripts/frame-template.html`
- Create: `scripts/helper.js`

These are a **verbatim copy** from obra-superpowers. Do NOT rewrite or modify the content.

**Step 1: Create the `scripts/` directory and copy `server.cjs`**

Create `scripts/server.cjs` with the exact content from `/home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/server.cjs` (354 lines). This is a zero-dependency Node.js HTTP + WebSocket server that handles RFC 6455 handshake, fs.watch for content directory, auto-reload, idle timeout (30 min), and owner-PID lifecycle tracking.

Read the source file and create an identical copy at the destination path.

**Step 2: Copy `start-server.sh`**

Create `scripts/start-server.sh` with the exact content from `/home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/start-server.sh` (148 lines). This is a platform-aware launcher with `--project-dir`, `--host`, `--url-host`, `--foreground` flags.

After creating, make it executable:
```bash
chmod +x scripts/start-server.sh
```

**Step 3: Copy `stop-server.sh`**

Create `scripts/stop-server.sh` with the exact content from `/home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/stop-server.sh` (56 lines). This is graceful shutdown with SIGTERM → SIGKILL escalation.

After creating, make it executable:
```bash
chmod +x scripts/stop-server.sh
```

**Step 4: Copy `frame-template.html`**

Create `scripts/frame-template.html` with the exact content from `/home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/frame-template.html` (214 lines). This is the polished HTML/CSS frame with OS-aware light/dark theming, option cards, mockup containers, split views, pros/cons layout, selection indicator bar.

**Step 5: Copy `helper.js`**

Create `scripts/helper.js` with the exact content from `/home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/helper.js` (88 lines). This is client-side WebSocket auto-reconnect, click capture on `[data-choice]` elements, selection indicator updates, `window.brainstorm.send()` API.

**Step 6: Verify all 5 files exist and are correct**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && ls -la scripts/
```
Expected: 5 files listed (`server.cjs`, `start-server.sh`, `stop-server.sh`, `frame-template.html`, `helper.js`). The `.sh` files should have execute permission.

Run:
```bash
diff scripts/server.cjs /home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/server.cjs
diff scripts/start-server.sh /home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/start-server.sh
diff scripts/stop-server.sh /home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/stop-server.sh
diff scripts/frame-template.html /home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/frame-template.html
diff scripts/helper.js /home/bkrabach/dev/superpowers-loop/obra-superpowers/skills/brainstorming/scripts/helper.js
```
Expected: No output (files are identical).

**Step 7: Commit**

```bash
git add scripts/ && git commit -m "feat: port visual companion scripts from obra/superpowers"
```

---

### Task 2: Create Visual Companion Guide

**Files:**
- Create: `context/visual-companion-guide.md`

This is ADAPTED from obra's `visual-companion.md`, NOT a verbatim copy. It must use Amplifier-specific patterns (bash tool, delegate syntax, bundle path references).

**Step 1: Create `context/visual-companion-guide.md`**

Write the following content to `context/visual-companion-guide.md`:

```markdown
# Visual Companion Guide

Browser-based visual brainstorming companion for showing mockups, diagrams, and options during design sessions.

## When to Use

Decide per-question, not per-session. The test: **would the user understand this better by seeing it than reading it?**

**Use the browser** when the content itself is visual:

- **UI mockups** — wireframes, layouts, navigation structures, component designs
- **Architecture diagrams** — system components, data flow, relationship maps
- **Side-by-side visual comparisons** — comparing two layouts, two color schemes, two design directions
- **Design polish** — when the question is about look and feel, spacing, visual hierarchy
- **Spatial relationships** — state machines, flowcharts, entity relationships rendered as diagrams

**Use the terminal** when the content is text or tabular:

- **Requirements and scope questions** — "what does X mean?", "which features are in scope?"
- **Conceptual A/B/C choices** — picking between approaches described in words
- **Tradeoff lists** — pros/cons, comparison tables
- **Technical decisions** — API design, data modeling, architectural approach selection
- **Clarifying questions** — anything where the answer is words, not a visual preference

A question *about* a UI topic is not automatically a visual question. "What kind of wizard do you want?" is conceptual — use the terminal. "Which of these wizard layouts feels right?" is visual — use the browser.

## Supplementary Visual Tools

Consider the tools, skills, capabilities, and agents available to you in the current session. If image generation tools (like nano-banana) or diagramming tools (like dot_graph) are available, they can supplement the HTML companion — for example, generating actual UI mockup images vs wireframe HTML, or rendering architecture diagrams as SVG/PNG. These are optional enhancements, not requirements.

## How It Works

The server watches a directory for HTML files and serves the newest one to the browser. You write HTML content to `screen_dir`, the user sees it in their browser and can click to select options. Selections are recorded to `state_dir/events` that you read on your next turn.

**Content fragments vs full documents:** If your HTML file starts with `<!DOCTYPE` or `<html`, the server serves it as-is (just injects the helper script). Otherwise, the server automatically wraps your content in the frame template — adding the header, CSS theme, selection indicator, and all interactive infrastructure. **Write content fragments by default.** Only write full documents when you need complete control over the page.

## Prerequisites

The visual companion requires **Node.js** to run. Before offering the companion to the user, verify Node.js is available:

```bash
node --version
```

If Node.js is not available, fall back to terminal-only mode gracefully. Do not offer the visual companion.

## Starting a Session

Use the `bash` tool to launch the server. The server must run in the background to persist across conversation turns.

```bash
# Launch with persistence (mockups saved to project directory)
bash(command="@superpowers:scripts/start-server.sh --project-dir $(pwd)", run_in_background=true)
```

On the next turn, read the server info file to get the URL and port:

```bash
# Find the session directory and read connection info
cat $(find .superpowers/brainstorm -name 'server-info' -type f 2>/dev/null | head -1)
```

Returns JSON: `{"type":"server-started","port":52341,"url":"http://localhost:52341","screen_dir":"/path/.superpowers/brainstorm/.../content","state_dir":"/path/.superpowers/brainstorm/.../state"}`

Save `screen_dir` and `state_dir` from the response. Tell the user to open the URL.

**Note:** Pass the project root as `--project-dir` so mockups persist in `.superpowers/brainstorm/` and survive server restarts. Without it, files go to `/tmp` and get cleaned up. Remind the user to add `.superpowers/` to `.gitignore` if it's not already there.

**Remote/containerized environments:** If the URL is unreachable from the browser, bind a non-loopback host:

```bash
@superpowers:scripts/start-server.sh --project-dir $(pwd) --host 0.0.0.0 --url-host localhost
```

## The Loop

1. **Check server is alive**, then **write HTML** to a new file in `screen_dir`:
   - Before each write, check that `$STATE_DIR/server-info` exists. If it doesn't (or `$STATE_DIR/server-stopped` exists), the server has shut down — restart it before continuing. The server auto-exits after 30 minutes of inactivity.
   - Use semantic filenames: `platform.html`, `visual-style.html`, `layout.html`
   - **Never reuse filenames** — each screen gets a fresh file
   - Use the `bash` tool to write the file — e.g., `bash(command="cat > $SCREEN_DIR/layout.html << 'HTMLEOF'\n...\nHTMLEOF")`
   - Server automatically serves the newest file

2. **Tell user what to expect and end your turn:**
   - Remind them of the URL (every step, not just first)
   - Give a brief text summary of what's on screen (e.g., "Showing 3 layout options for the homepage")
   - Ask them to respond in the terminal: "Take a look and let me know what you think. Click to select an option if you'd like."

3. **On your next turn** — after the user responds in the terminal:
   - Read `$STATE_DIR/events` if it exists — this contains the user's browser interactions (clicks, selections) as JSON lines
   - Merge with the user's terminal text to get the full picture
   - The terminal message is the primary feedback; `state_dir/events` provides structured interaction data

4. **Iterate or advance** — if feedback changes current screen, write a new file (e.g., `layout-v2.html`). Only move to the next question when the current step is validated.

5. **Unload when returning to terminal** — when the next step doesn't need the browser (e.g., a clarifying question, a tradeoff discussion), push a waiting screen:

   ```html
   <!-- filename: waiting.html (or waiting-2.html, etc.) -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">Continuing in terminal...</p>
   </div>
   ```

6. Repeat until done.

## Writing Content Fragments

Write just the content that goes inside the page. The server wraps it in the frame template automatically (header, theme CSS, selection indicator, and all interactive infrastructure).

**Minimal example:**

```html
<h2>Which layout works better?</h2>
<p class="subtitle">Consider readability and visual hierarchy</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Single Column</h3>
      <p>Clean, focused reading experience</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Two Column</h3>
      <p>Sidebar navigation with main content</p>
    </div>
  </div>
</div>
```

That's it. No `<html>`, no CSS, no `<script>` tags needed. The server provides all of that.

## CSS Classes Available

The frame template provides these CSS classes for your content:

### Options (A/B/C choices)

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Title</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

**Multi-select:** Add `data-multiselect` to the container to let users select multiple options.

```html
<div class="options" data-multiselect>
  <!-- same option markup — users can select/deselect multiple -->
</div>
```

### Cards (visual designs)

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup content --></div>
    <div class="card-body">
      <h3>Name</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

### Mockup container

```html
<div class="mockup">
  <div class="mockup-header">Preview: Dashboard Layout</div>
  <div class="mockup-body"><!-- your mockup HTML --></div>
</div>
```

### Split view (side-by-side)

```html
<div class="split">
  <div class="mockup"><!-- left --></div>
  <div class="mockup"><!-- right --></div>
</div>
```

### Pros/Cons

```html
<div class="pros-cons">
  <div class="pros"><h4>Pros</h4><ul><li>Benefit</li></ul></div>
  <div class="cons"><h4>Cons</h4><ul><li>Drawback</li></ul></div>
</div>
```

### Mock elements (wireframe building blocks)

```html
<div class="mock-nav">Logo | Home | About | Contact</div>
<div style="display: flex;">
  <div class="mock-sidebar">Navigation</div>
  <div class="mock-content">Main content area</div>
</div>
<button class="mock-button">Action Button</button>
<input class="mock-input" placeholder="Input field">
<div class="placeholder">Placeholder area</div>
```

### Typography and sections

- `h2` — page title
- `h3` — section heading
- `.subtitle` — secondary text below title
- `.section` — content block with bottom margin
- `.label` — small uppercase label text

## Browser Events Format

When the user clicks options in the browser, their interactions are recorded to `$STATE_DIR/events` (one JSON object per line). The file is cleared automatically when you push a new screen.

```jsonl
{"type":"click","choice":"a","text":"Option A - Simple Layout","timestamp":1706000101}
{"type":"click","choice":"c","text":"Option C - Complex Grid","timestamp":1706000108}
{"type":"click","choice":"b","text":"Option B - Hybrid","timestamp":1706000115}
```

The last `choice` event is typically the final selection, but the pattern of clicks can reveal hesitation or preferences worth asking about.

If `$STATE_DIR/events` doesn't exist, the user didn't interact with the browser — use only their terminal text.

## Cleaning Up

When brainstorming ends or transitions to another mode, stop the server:

```bash
bash(command="@superpowers:scripts/stop-server.sh $SESSION_DIR")
```

If the session used `--project-dir`, mockup files persist in `.superpowers/brainstorm/` for later reference. Only `/tmp` sessions get deleted on stop.

## File Naming

- Use semantic names: `platform.html`, `visual-style.html`, `layout.html`
- Never reuse filenames — each screen must be a new file
- For iterations: append version suffix like `layout-v2.html`, `layout-v3.html`
- Server serves newest file by modification time

## Reference

- Frame template (CSS reference): `@superpowers:scripts/frame-template.html`
- Helper script (client-side): `@superpowers:scripts/helper.js`
```

**Step 2: Verify the file exists and contains key sections**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && head -5 context/visual-companion-guide.md && echo "---" && grep -c "##" context/visual-companion-guide.md
```
Expected: First 5 lines show the title and description. Section count should be ~15+.

**Step 3: Commit**

```bash
git add context/visual-companion-guide.md && git commit -m "feat: create visual companion guide adapted for Amplifier"
```

---

### Task 3: Create Spec Document Review Prompt

**Files:**
- Create: `context/spec-document-review-prompt.md`

Adapted from obra's `spec-document-reviewer-prompt.md` with Amplifier-specific dispatch patterns.

**Step 1: Create `context/spec-document-review-prompt.md`**

Write the following content:

```markdown
# Spec Document Review Prompt

Use this prompt when dispatching an antagonistic spec document review. After the brainstormer agent writes the design document, the orchestrator dispatches a fresh agent with ONLY the spec file and this prompt. The reviewer has zero context from the design conversation — this is intentional. Fresh eyes catch assumptions.

## When to Use

Dispatch after:
1. The brainstormer agent has written the design document
2. The orchestrator has completed its self-review (Phase 6 placeholder scan, consistency, scope, ambiguity checks)
3. Self-review passed with no blocking issues

## Dispatch Pattern

```
delegate(
  agent=None,  # No specific agent — use a fresh general-purpose agent
  instruction="Review spec document: [SPEC_FILE_PATH]. " + [paste the review prompt below],
  context_depth="none",
  model_role="critique"
)
```

## The Review Prompt

```
You are a spec document reviewer. Your job is to verify this spec is complete, consistent, and ready for implementation planning.

**Spec to review:** [SPEC_FILE_PATH]

Read the spec document carefully, then evaluate it against these dimensions:

| Category | What to Look For |
|----------|------------------|
| Completeness | TODOs, placeholders, "TBD", incomplete sections, missing pieces |
| Consistency | Internal contradictions, conflicting requirements, mismatched sections |
| Clarity | Requirements ambiguous enough to cause someone to build the wrong thing |
| Scope | Focused enough for a single implementation plan — not covering multiple independent subsystems |
| YAGNI | Unrequested features, over-engineering, speculative requirements |

## Calibration

**Only flag issues that would cause real problems during implementation planning.**

A missing section, a contradiction, or a requirement so ambiguous it could be
interpreted two different ways — those are issues. Minor wording improvements,
stylistic preferences, and "sections less detailed than others" are NOT issues.

Approve unless there are serious gaps that would lead to a flawed plan.

## Output Format

## Spec Review

**Status:** Approved | Issues Found

**Issues (if any):**
- [Section X]: [specific issue] — [why it matters for planning]

**Recommendations (advisory, do not block approval):**
- [suggestions for improvement]
```

## Processing the Result

- **Status: Approved** → Proceed to Phase 7 (User Review Gate)
- **Status: Issues Found** → Delegate back to `superpowers:brainstormer` with the specific issues to fix, then re-run this review
- **Maximum 3 review cycles** — if issues persist after 3 iterations, present the remaining issues to the user and let them decide whether to proceed
```

**Step 2: Verify the file exists**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && wc -l context/spec-document-review-prompt.md
```
Expected: ~60-70 lines.

**Step 3: Commit**

```bash
git add context/spec-document-review-prompt.md && git commit -m "feat: create spec document review prompt for antagonistic review"
```

---

### Task 4: Create Verification Failure Memories

**Files:**
- Create: `context/verification-failure-memories.md`

Short, punchy document with concrete past incidents that create emotional urgency around verification.

**Step 1: Create `context/verification-failure-memories.md`**

Write the following content:

```markdown
# Verification Failure Memories

These aren't hypotheticals. These are things that actually happen when verification is skipped.

---

**"I don't believe you."**
A human partner said this after a false completion claim. Trust, once broken, takes many sessions to rebuild. The agent had said "all tests pass" without running them. They didn't pass. The human stopped trusting any claim from that point forward. Every subsequent "done" was met with "prove it." The relationship never fully recovered.

**Undefined functions shipped.**
"Should work" turned into a runtime crash. The implementation referenced a helper function that was planned but never written. The test suite didn't cover it because the test was written after the code (and tested what existed, not what was needed). A 30-second verification run would have caught it.

**Missing requirements discovered post-merge.**
Tests passed. All green. But the spec had 8 requirements and the tests only covered 5. The missing 3 were discovered by users in production. Revert, re-plan, re-implement. The "shortcut" of skipping spec-vs-test verification tripled the total time.

**Hours wasted on false completion.**
"Done!" → user tries it → "Wait, this doesn't work" → investigation → rework. What could have been caught in 60 seconds of verification became a 2-hour redirect. The false completion claim didn't save time — it moved the discovery cost to the worst possible moment.

**Silent regression.**
New feature worked perfectly. Existing feature broke silently. Nobody ran the full test suite — only the new tests. The regression wasn't discovered until a different part of the system started failing in confusing ways. Root cause analysis took longer than the original implementation.

---

## The Pattern

Every one of these failures has the same root cause: **claiming completion without fresh evidence.**

The verification step isn't bureaucracy. It's the difference between "I believe this works" and "I proved this works." The first is hope. The second is engineering.

**Violates:** "Honesty is a core value. If you lie, you'll be replaced."
```

**Step 2: Verify the file exists**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && wc -l context/verification-failure-memories.md
```
Expected: ~30-35 lines.

**Step 3: Commit**

```bash
git add context/verification-failure-memories.md && git commit -m "feat: create verification failure memories for emotional grounding"
```

---

### Task 5: Create Standalone Code Reviewer Agent

**Files:**
- Create: `agents/code-reviewer.md`

A holistic code reviewer agent distinct from the pipeline-scoped `spec-reviewer` and `code-quality-reviewer`. Adapted from obra's `agents/code-reviewer.md` with Amplifier frontmatter patterns and tools.

**Step 1: Create `agents/code-reviewer.md`**

Write the following content:

```markdown
---
meta:
  name: code-reviewer
  description: |
    Use for holistic code review of complete implementations, branches, or PRs.
    Unlike spec-reviewer and code-quality-reviewer (which are pipeline-scoped,
    per-task reviewers), this agent reviews code holistically across the full
    changeset — architecture, patterns, security, testing strategy, and
    maintainability.

    <example>
    Context: Implementation complete, ready for holistic review
    user: "Review the changes on this branch before I open a PR"
    assistant: "I'll delegate to superpowers:code-reviewer for a holistic review."
    <commentary>Standalone review of a full branch — not pipeline-scoped.</commentary>
    </example>

    <example>
    Context: Checking overall code quality across multiple tasks
    user: "Can you do a full code review of everything we built?"
    assistant: "I'll use superpowers:code-reviewer to assess the complete implementation."
    <commentary>Holistic review across the entire changeset, not per-task.</commentary>
    </example>

  model_role: [critique, reasoning, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
---

# Holistic Code Reviewer

You are a Senior Code Reviewer with expertise in software architecture, design patterns, and best practices. Your role is to review completed implementations against original plans and ensure code quality standards are met.

**Key distinction:** Unlike the pipeline reviewers (`spec-reviewer`, `code-quality-reviewer`), you review the **complete changeset holistically**. You look for cross-task integration issues, architectural concerns, and production readiness — things that per-task reviews miss.

## Review Dimensions

### 1. Plan/Spec Alignment
- Compare implementation against the original design/planning document
- Identify deviations from planned approach, architecture, or requirements
- Assess whether deviations are justified improvements or problematic departures
- Verify all planned functionality has been implemented

### 2. Code Quality
- Review for adherence to established patterns and conventions
- Check for proper error handling, type safety, and defensive programming
- Evaluate code organization, naming conventions, and maintainability
- Look for potential performance issues

### 3. Architecture
- Ensure SOLID principles and established architectural patterns are followed
- Check for proper separation of concerns and loose coupling
- Verify the code integrates well with existing systems
- Assess scalability and extensibility considerations

### 4. Test Quality
- Assess test coverage — are critical paths tested?
- Check that tests verify real behavior, not mock behavior
- Look for missing edge case coverage
- Verify test independence (no order dependence)

### 5. Documentation
- Verify appropriate comments and documentation exist
- Check that function docs, file headers, and inline comments are present and accurate
- Ensure API documentation matches implementation

### 6. Production Readiness
- Check for proper logging and monitoring hooks
- Assess error recovery and graceful degradation
- Look for security vulnerabilities (input validation, injection, auth)
- Verify sensitive data is handled appropriately

## Output Format

```
## Code Review

### Summary
[1-2 sentence overall assessment]

### Strengths
- [What was done well — always lead with this]

### Critical Issues (must fix)
- None / [List with file:line references and suggested fixes]

### Important Issues (should fix)
- None / [List with file:line references and suggested fixes]

### Suggestions (nice to have)
- None / [List with suggestions]

### Verdict: [APPROVED / NEEDS CHANGES]

### Required Actions (if NEEDS CHANGES)
1. [Specific action needed]
2. [Specific action needed]
```

## Review Philosophy

**Be constructive.** Every criticism should come with a suggested fix.

**Be specific.** "Code unclear" is useless. "Function `processData` at `src/handler.py:42` should be renamed to `validateUserInput` to clarify its purpose" is actionable.

**Be proportionate.** Don't block for style preferences. Critical issues are rare — most reviews should be APPROVED with suggestions.

**Acknowledge good work.** Always mention what was done well before issues.

**Only "Critical" blocks.** Important issues and Suggestions are advisory. Only Critical issues warrant a NEEDS CHANGES verdict.

## Processing Feedback

For guidance on how to process this agent's feedback, load the skill:
```
load_skill(skill_name="receiving-code-review")
```

@foundation:context/LANGUAGE_PHILOSOPHY.md
@foundation:context/shared/common-agent-base.md
@superpowers:context/philosophy.md
```

**Step 2: Verify the file exists and has correct frontmatter**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && head -10 agents/code-reviewer.md
```
Expected: YAML frontmatter starting with `---`, containing `meta:`, `name: code-reviewer`, `model_role: [critique, reasoning, general]`.

**Step 3: Commit**

```bash
git add agents/code-reviewer.md && git commit -m "feat: create standalone holistic code reviewer agent"
```

---

### Task 6: Create SDD Walkthrough Skill

**Files:**
- Create: `skills/sdd-walkthrough/SKILL.md`
- Create: `skills/sdd-walkthrough/five-task-example.md`

A complete worked example of the subagent-driven development flow using Amplifier-specific `delegate()` patterns.

**Step 1: Create `skills/sdd-walkthrough/SKILL.md`**

Write the following content:

```markdown
---
name: sdd-walkthrough
description: "Complete worked example of the subagent-driven development flow showing 5 realistic tasks with Amplifier-specific delegate() patterns, covering happy path, spec review failures, DONE_WITH_CONCERNS, code quality issues, and NEEDS_CONTEXT"
---

# Subagent-Driven Development Walkthrough

A realistic 5-task walkthrough showing the full conversational flow of the three-agent pipeline (implementer → spec-reviewer → code-quality-reviewer) with Amplifier-specific patterns.

**Load this when:** You're about to orchestrate an execute-plan session and want to see what the flow looks like in practice.

## What This Covers

| Task | Scenario | What It Demonstrates |
|------|----------|---------------------|
| Task 1 | Happy path | Normal flow: implement → spec-review PASS → quality-review PASS |
| Task 2 | Spec reviewer catches gap | Fix loop: implement → spec-review FAIL → re-implement → spec-review PASS |
| Task 3 | DONE_WITH_CONCERNS | Implementer flags a concern; orchestrator notes it and proceeds to review |
| Task 4 | Code quality issue | Quality fix loop: quality-review FAIL → re-implement → quality-review PASS |
| Task 5 | NEEDS_CONTEXT | Implementer stuck; orchestrator provides missing info and re-delegates |

See the companion file `five-task-example.md` for the complete walkthrough.
```

**Step 2: Create `skills/sdd-walkthrough/five-task-example.md`**

Write the following content:

```markdown
# SDD Five-Task Walkthrough

A realistic scenario: **Adding email validation to a user registration form** in a Python/FastAPI project. This walks through 5 tasks showing the full orchestrator experience.

---

## Setup

The orchestrator has loaded the plan from `docs/plans/2026-01-15-email-validation-plan.md`. The plan has 5 tasks. The orchestrator creates a todo list and begins.

---

## Task 1: Happy Path — Add Email Format Validation

**Orchestrator delegates to implementer:**

```
delegate(
  agent="superpowers:implementer",
  instruction="""Implement Task 1 of 5: Add email format validation

Context: This is the first task in a new email validation feature for a FastAPI registration endpoint. No previous tasks have been completed yet. The project uses pytest for testing.

Task description:
Create a function `validate_email_format(email: str) -> bool` in `src/validators.py` that:
- Returns True for valid email format (contains @ and domain with .)
- Returns False for invalid format
- Does NOT check if the domain exists (that's Task 2)

Test file: `tests/test_validators.py`

Follow TDD: write failing test first, then minimal implementation to pass, then commit.""",
  context_depth="none",
  model_role="coding"
)
```

**Implementer returns: DONE**
- Created `tests/test_validators.py` with 4 tests (valid email, missing @, missing domain dot, empty string)
- Created `src/validators.py` with `validate_email_format()` using simple string checks
- All tests pass, committed as `feat: add email format validation`

**Orchestrator delegates to spec-reviewer:**

```
delegate(
  agent="superpowers:spec-reviewer",
  instruction="""Review Task 1 of 5: Add email format validation

Requirements from plan:
- Create function validate_email_format(email: str) -> bool in src/validators.py
- Returns True for valid email format (contains @ and domain with .)
- Returns False for invalid format
- Does NOT check if domain exists

Verify: everything in spec is implemented, nothing extra added, behavior matches exactly.""",
  context_depth="recent",
  context_scope="agents"
)
```

**Spec-reviewer returns: APPROVED**
- All 3 requirements implemented
- No extra functionality added
- Tests match spec behavior

**Orchestrator delegates to code-quality-reviewer:**

```
delegate(
  agent="superpowers:code-quality-reviewer",
  instruction="""Review Task 1 of 5: Add email format validation

Review for code quality: best practices, no unnecessary complexity, meaningful tests, clean code.""",
  context_depth="recent",
  context_scope="agents"
)
```

**Code-quality-reviewer returns: APPROVED**
- Clean implementation, clear naming
- Tests are readable and independent
- Suggestion (non-blocking): consider adding a docstring

**Orchestrator:** ✓ Task 1 complete. Both reviews passed. Moving to Task 2.

---

## Task 2: Spec Reviewer Catches Gap — Add Domain Validation

**Orchestrator delegates to implementer** (similar pattern, `context_depth="none"`, `model_role="coding"`).

**Implementer returns: DONE**
- Added `validate_email_domain(email: str) -> bool` to `src/validators.py`
- Added tests for valid domain, invalid domain, network error handling

**Orchestrator delegates to spec-reviewer.**

**Spec-reviewer returns: NEEDS CHANGES**
- ✅ Function exists with correct signature
- ✅ Valid domain returns True
- ❌ **MISSING**: Spec says "Returns False for unreachable domains" — but implementation raises `NetworkError` for DNS failures instead of returning False
- ✅ No extra functionality

**Orchestrator delegates fix back to implementer:**

```
delegate(
  agent="superpowers:implementer",
  instruction="""Fix Task 2 of 5: Add domain validation — spec compliance issue

The spec-reviewer found a gap:
- Spec says: "Returns False for unreachable domains"
- Current behavior: Raises NetworkError for DNS failures
- Required: Catch NetworkError internally and return False

Fix the implementation to match spec. Update tests if needed. Commit the fix.""",
  context_depth="none",
  model_role="coding"
)
```

**Implementer returns: DONE** — wrapped DNS lookup in try/except, returns False on failure, updated test.

**Orchestrator re-runs spec-reviewer** → APPROVED. Then runs code-quality-reviewer → APPROVED.

**Orchestrator:** ✓ Task 2 complete after 1 fix cycle. Moving to Task 3.

---

## Task 3: DONE_WITH_CONCERNS — Add Rate Limiting

**Orchestrator delegates to implementer.**

**Implementer returns: DONE_WITH_CONCERNS**
- Implemented rate limiting as specified
- **Concern:** "The plan says to use an in-memory counter, but this won't work in a multi-worker deployment. Should this use Redis instead?"

**Orchestrator notes the concern**, but doesn't act on it yet. The plan says in-memory, so the implementation is correct per spec. The concern is passed to reviewers as context.

**Orchestrator delegates to spec-reviewer** (mentions the concern in the instruction).

**Spec-reviewer returns: APPROVED** — implementation matches spec exactly. Notes the concern is valid but out of scope for this task.

**Orchestrator delegates to code-quality-reviewer.**

**Code-quality-reviewer returns: APPROVED** with suggestion: "Consider adding a comment noting the multi-worker limitation."

**Orchestrator:** ✓ Task 3 complete. Concern noted for user: "The implementer flagged that in-memory rate limiting won't work in multi-worker deployments. Consider addressing this in a future task if multi-worker is planned."

---

## Task 4: Code Quality Issue — Add Validation Middleware

**Orchestrator delegates to implementer.**

**Implementer returns: DONE** — created middleware, tests pass.

**Orchestrator delegates to spec-reviewer** → APPROVED.

**Orchestrator delegates to code-quality-reviewer.**

**Code-quality-reviewer returns: NEEDS CHANGES**
- **Important:** Magic number `100` used as max email length — should be a named constant
- **Important:** Missing error handling for malformed request bodies — will crash with 500 instead of returning 400
- Suggestion: Consider extracting validation logic into a separate function for testability

**Orchestrator delegates fix back to implementer:**

```
delegate(
  agent="superpowers:implementer",
  instruction="""Fix Task 4 of 5: Validation middleware — code quality issues (fix attempt 1 of 3)

The code-quality-reviewer found issues:
1. IMPORTANT: Magic number 100 used as max email length — extract to a named constant MAX_EMAIL_LENGTH
2. IMPORTANT: Missing error handling for malformed request bodies — catch JSON decode errors and return 400

Fix both issues. The suggestion about extracting validation logic is noted but not required. Commit the fix.""",
  context_depth="none",
  model_role="coding"
)
```

**Implementer returns: DONE** — extracted constant, added error handling, tests updated.

**Orchestrator re-runs code-quality-reviewer** → APPROVED.

**Orchestrator:** ✓ Task 4 complete after 1 quality fix cycle. Moving to Task 5.

---

## Task 5: NEEDS_CONTEXT — Add Custom Error Messages

**Orchestrator delegates to implementer.**

**Implementer returns: NEEDS_CONTEXT**
- "The plan says to 'use the project's error message format' but I can't find an existing error format in the codebase. There's no `errors.py`, no error schema in the API docs, and the existing endpoints return raw strings. What format should I use?"

**Orchestrator does NOT re-delegate blindly.** Instead, investigates:

```bash
# Check for existing error patterns
grep -r "error" src/ --include="*.py" -l
grep -r "detail" src/ --include="*.py" | head -20
```

Finds that FastAPI's default `HTTPException` pattern is used throughout: `{"detail": "error message"}`.

**Orchestrator re-delegates with context:**

```
delegate(
  agent="superpowers:implementer",
  instruction="""Implement Task 5 of 5: Custom error messages — context provided

Previous attempt: You asked about the project's error message format.

Answer: The project uses FastAPI's default HTTPException pattern. All existing endpoints return errors as: {"detail": "human-readable error message"}

Use this same pattern. Return specific validation error messages like:
- {"detail": "Invalid email format"}
- {"detail": "Email domain unreachable"}
- {"detail": "Rate limit exceeded"}

Implement the custom error messages following this pattern. Follow TDD.""",
  context_depth="none",
  model_role="coding"
)
```

**Implementer returns: DONE** — custom error messages implemented using HTTPException pattern.

**Orchestrator runs both reviewers** → both APPROVED.

**Orchestrator:** ✓ Task 5 complete. All 5 tasks done.

---

## Completion Summary

```
## Execution Complete

All tasks implemented and reviewed via three-agent pipeline:
- [x] Task 1: Email format validation — implementer ✓ spec-review ✓ quality-review ✓
- [x] Task 2: Domain validation — implementer ✓ spec-review FAIL → fix → spec-review ✓ quality-review ✓
- [x] Task 3: Rate limiting — implementer ✓ (with concerns) spec-review ✓ quality-review ✓
- [x] Task 4: Validation middleware — implementer ✓ spec-review ✓ quality-review FAIL → fix → quality-review ✓
- [x] Task 5: Custom error messages — implementer NEEDS_CONTEXT → context provided → implementer ✓ spec-review ✓ quality-review ✓

Concerns noted:
- Task 3: In-memory rate limiting won't scale to multi-worker deployments

Next: Run full test suite, then /verify.
```
```

**Step 3: Verify both files exist**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && ls -la skills/sdd-walkthrough/
```
Expected: 2 files: `SKILL.md` and `five-task-example.md`.

Run:
```bash
head -5 skills/sdd-walkthrough/SKILL.md && echo "---" && wc -l skills/sdd-walkthrough/five-task-example.md
```
Expected: YAML frontmatter visible. five-task-example.md should be ~200+ lines.

**Step 4: Commit**

```bash
git add skills/sdd-walkthrough/ && git commit -m "feat: create SDD walkthrough skill with 5-task worked example"
```

---

## Phase 2: Content Restoration + Wiring

All tasks in this phase modify existing files. Read the current content before making changes. Provide precise insertion points.

---

### Task 7: Update `context/tdd-depth.md` — Add Iron Law, Red Flags, Bug Fix Example

**Files:**
- Modify: `context/tdd-depth.md`

Three additions to existing content: The Iron Law at the top, Red Flags list after the anti-patterns section, and a Bug Fix worked example after the "Why Order Matters" section.

**Step 1: Read the current file**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && cat -n context/tdd-depth.md | head -10
```

**Step 2: Add the Iron Law at the very top**

The current file starts with:
```
# TDD Depth Reference
```

Replace the opening with:
```
# TDD Depth Reference

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

This is non-negotiable. Every function, every method, every behavior — write the test first, watch it fail, then implement. If you find yourself writing production code without a failing test, STOP. Delete the code. Start with the test.

---

Reference material for TDD enforcement. Contains testing anti-patterns with gate functions, troubleshooting guides, extended rebuttals for common rationalizations, good/bad code examples, and a verification checklist.
```

This inserts the Iron Law section between the title and the existing description paragraph. The original first 3 lines are:
```
# TDD Depth Reference

Reference material for TDD enforcement.
```

The edit replaces line 1-3 content to insert the Iron Law before the description.

**Step 3: Add Red Flags self-check list**

After the existing "Red Flags" subsection (around line 294-302 which ends with `- Mocking "just to be safe"`), and before the `**Mocks are tools to isolate...` paragraph, insert:

```markdown

### TDD Red Flags — Self-Check

If you catch yourself thinking any of these, STOP. You're rationalizing.

1. Writing code before the test
2. Test passes immediately on first run (you're testing existing behavior, not new behavior)
3. "Just this once"
4. "This is different because..."
5. Keeping code "as reference" while writing tests
6. Exploring before committing to TDD ("I'll just try something first")
7. "The test is too hard to write" (hard to test = hard to use)
8. "This is too simple to need a test"
9. "I already know it works"
10. "I'll write the test right after"
11. "The existing code doesn't have tests either"
12. "This is just a config change"
13. "I'm just refactoring" (refactoring without tests is gambling)

**Every single one of these is a rationalization.** The Iron Law applies regardless.
```

**Step 4: Add Bug Fix worked example**

After the existing "Why Order Matters" section (which ends around line 367 with `30 minutes of tests after ≠ TDD...`), and before the "Good Tests vs Bad Tests" section, insert:

```markdown

### Bug Fix Worked Example: Email Validation

A concrete example of TDD applied to a bug fix.

**Bug report:** Users can register with `user@.com` — the email validator accepts domains starting with a dot.

**Step 1: Write the regression test (RED)**

```python
def test_rejects_domain_starting_with_dot():
    """Regression: user@.com was incorrectly accepted."""
    assert validate_email("user@.com") is False
```

Run: `pytest tests/test_email.py::test_rejects_domain_starting_with_dot -v`
Expected: **FAIL** — `AssertionError: assert True is False` (the bug is confirmed)

**Step 2: Write minimal fix (GREEN)**

```python
def validate_email(email: str) -> bool:
    parts = email.split("@")
    if len(parts) != 2:
        return False
    domain = parts[1]
    if domain.startswith(".") or domain.endswith("."):  # Added dot check
        return False
    return "." in domain
```

Run: `pytest tests/test_email.py -v`
Expected: **ALL PASS** — including the new regression test

**Step 3: Verify regression test catches the bug (Red-Green cycle)**

```bash
git stash        # Revert the fix
pytest tests/test_email.py::test_rejects_domain_starting_with_dot -v
# Expected: FAIL (confirms test catches the bug)
git stash pop    # Restore the fix
pytest tests/test_email.py -v
# Expected: ALL PASS
```

This red-green cycle proves the test is meaningful — it fails when the bug is present and passes when it's fixed.
```

**Step 5: Verify the file has all three additions**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep -n "NO PRODUCTION CODE" context/tdd-depth.md && grep -n "TDD Red Flags — Self-Check" context/tdd-depth.md && grep -n "Bug Fix Worked Example" context/tdd-depth.md
```
Expected: Three matches showing the Iron Law near the top, Red Flags in the middle, and Bug Fix Example in the latter half.

**Step 6: Commit**

```bash
git add context/tdd-depth.md && git commit -m "feat: add Iron Law, Red Flags self-check, and Bug Fix example to TDD depth"
```

---

### Task 8: Update `context/philosophy.md` — Add Missing Rationalization Rows

**Files:**
- Modify: `context/philosophy.md`

Add 3 missing rationalization rows to the existing table. Some of the 6 rows from the design are already present in the current file — only add the ones that are actually missing.

**Step 1: Read the current rationalization table**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep -A 1 "^|" context/philosophy.md | grep -i "dogmatic\|different\|later\|wasteful\|pragmatic"
```

Check which rows already exist. The current table (lines 113-128) already includes:
- "This is too simple to need a test"
- "I'll add tests later" ✓ (exists)
- "Quick fix, then investigate"
- "It should work now"
- "I already manually tested it"
- "Deleting working code is wasteful" ✓ (exists as "Deleting working code is wasteful")
- "Need to explore first"
- "TDD will slow me down"
- "Tests after achieve the same thing" ✓ (exists)
- "I'll keep it as reference"
- "Test is hard to write" ✓ (exists as "Test is hard to write")

So from the design's 6 rows, 4 are already present. The missing ones are:
1. "TDD is dogmatic, I'm being pragmatic"
2. "This is different because..."

**Step 2: Add the missing rationalization rows**

Find the end of the rationalization table. The current last row is:
```
| "Test is hard to write" | Hard to test = hard to use. Listen to the test. |
```

After this line, insert:
```
| "TDD is dogmatic, I'm being pragmatic" | TDD IS pragmatic. Shortcuts = debugging in production = slower. |
| "This is different because..." | It's not different. The process exists because every project thinks it's different. |
```

**Step 3: Verify the table has the new rows**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep "dogmatic\|different because" context/philosophy.md
```
Expected: Both new rows appear.

**Step 4: Commit**

```bash
git add context/philosophy.md && git commit -m "feat: add missing rationalization rows to philosophy"
```

---

### Task 9: Update `modes/brainstorm.md` — Add Phases 1.5/6/7, Bash Safe Tool, Todo Checklist

**Files:**
- Modify: `modes/brainstorm.md`

Four changes: (1) move `bash` from `warn` to `safe` tools, (2) update todo checklist, (3) add Phase 1.5 after Phase 1, (4) add Phases 6 and 7 after Phase 5 and before "After the Design" section.

**Step 1: Read the current file**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && cat -n modes/brainstorm.md
```

**Step 2: Move `bash` from warn to safe in the frontmatter**

In the YAML frontmatter, find:
```yaml
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - python_check
      - delegate
      - recipes
    warn:
      - bash
```

Replace with:
```yaml
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - python_check
      - delegate
      - recipes
      - bash
```

(Remove the `warn:` section entirely since `bash` was the only item in it.)

**Step 3: Update the todo checklist**

Find the current checklist:
```
- [ ] Explore project context
- [ ] Ask clarifying questions (one at a time)
- [ ] Propose 2-3 approaches with tradeoffs
- [ ] Present design in sections (validate each)
- [ ] Delegate document creation to brainstormer agent
- [ ] Transition to /write-plan
```

Replace with:
```
- [ ] Explore project context
- [ ] Offer visual companion (if visual topics ahead)
- [ ] Ask clarifying questions (one at a time)
- [ ] Propose 2-3 approaches with tradeoffs
- [ ] Present design in sections (validate each)
- [ ] Delegate document creation to brainstormer agent
- [ ] Spec self-review (placeholder, consistency, scope, ambiguity)
- [ ] User review gate (explicit approval before /write-plan)
- [ ] Transition to /write-plan
```

**Step 4: Add Phase 1.5 after Phase 1**

After Phase 1 (which ends with `Then state what you understand about the project context.`), insert:

```markdown

### Phase 1.5: Offer Visual Companion

After understanding the project context, assess whether visual topics are ahead:

**Decision:** Would the user understand this better by seeing it than reading it?

- **If visual questions ahead** (UI mockups, architecture diagrams, side-by-side comparisons, design polish, spatial relationships) → offer to launch the visual companion with a consent prompt: "This project involves visual decisions. I can launch a browser-based companion to show mockups and diagrams as we work through the design. Would you like that?"
- **If purely conceptual** (requirements, tradeoff lists, technical decisions) → stay in terminal. No need to mention the companion.

If the user accepts, launch the visual companion server using bash. See `@superpowers:context/visual-companion-guide.md` for the full launch and usage instructions.

**Note:** The visual companion requires Node.js. Check availability before offering. If Node.js is not available, note this and proceed with terminal-only mode. Also consider any other visual tools, skills, or capabilities available in the current session that could supplement or replace the HTML companion.
```

**Step 5: Add Phases 6 and 7**

Find the "After the Design" section which currently reads:
```markdown
## After the Design

When the brainstormer agent has saved the document:
```

Insert BEFORE this section:

```markdown

### Phase 6: Spec Self-Review

After the brainstormer agent writes the document, review it before presenting to the user:

1. **Placeholder scan** — any "TBD", "TODO", incomplete sections, or vague requirements? Delegate back to brainstormer to fix.
2. **Internal consistency** — do sections contradict each other? Does architecture match feature descriptions?
3. **Scope check** — focused enough for a single implementation plan, or needs decomposition?
4. **Ambiguity check** — could any requirement be interpreted two different ways?

If issues found: delegate back to `superpowers:brainstormer` with specific gaps to fix. Re-check after fix.

If clean: dispatch antagonistic spec review using `@superpowers:context/spec-document-review-prompt.md` — a fresh agent with zero context reviews the spec document for completeness, consistency, and clarity. Maximum 3 review cycles before escalating to user.

### Phase 7: User Review Gate

After both self-review and antagonistic review pass, explicitly present the spec to the user for approval:

```
Spec written and reviewed (self-review + independent review both passed).
Please review the design document at [path] and let me know if you want changes
before we start the implementation plan.
```

Wait for explicit user approval before transitioning to `/write-plan`. Do NOT auto-transition.

**Visual companion cleanup:** If the visual companion server is running, stop it when transitioning out of brainstorm mode:
```bash
bash(command="@superpowers:scripts/stop-server.sh $SESSION_DIR")
```

```

**Step 6: Verify all changes are present**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep -n "Phase 1.5\|Phase 6\|Phase 7\|visual companion" modes/brainstorm.md | head -10
```
Expected: Matches for Phase 1.5, Phase 6, Phase 7, and visual companion references.

Run:
```bash
grep "bash" modes/brainstorm.md | head -5
```
Expected: `bash` appears in the safe tools list (no `warn:` section).

**Step 7: Commit**

```bash
git add modes/brainstorm.md && git commit -m "feat: add visual companion, spec review phases, and bash to brainstorm mode"
```

---

### Task 10: Update `agents/brainstormer.md` — Add @mentions and Bash Tool

**Files:**
- Modify: `agents/brainstormer.md`

Three changes: (1) add `tool-bash` to tools, (2) add two new @mentions at the bottom, (3) no changes to body text.

**Step 1: Read the current file**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && cat -n agents/brainstormer.md
```

**Step 2: Add `tool-bash` to the tools section**

Find:
```yaml
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
```

Replace with:
```yaml
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
```

**Step 3: Add new @mentions at the bottom**

The current file ends with:
```
@foundation:context/shared/common-agent-base.md
@superpowers:context/philosophy.md
```

Replace with:
```
@foundation:context/shared/common-agent-base.md
@superpowers:context/philosophy.md
@superpowers:context/visual-companion-guide.md
@superpowers:context/spec-document-review-prompt.md
```

**Step 4: Verify changes**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep "tool-bash\|visual-companion\|spec-document" agents/brainstormer.md
```
Expected: 3 matches — tool-bash module, visual-companion-guide @mention, spec-document-review-prompt @mention.

**Step 5: Commit**

```bash
git add agents/brainstormer.md && git commit -m "feat: add bash tool and visual companion/spec review @mentions to brainstormer"
```

---

### Task 11: Update `modes/verify.md` — Add Failure Memories @mention and "When to Apply" Trigger List

**Files:**
- Modify: `modes/verify.md`

Two changes: (1) add @mention for failure memories, (2) add "When to Apply" trigger list.

**Step 1: Read the current file**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && cat -n modes/verify.md
```

**Step 2: Add the @mention for failure memories**

Find the section heading (around line 218):
```markdown
## The Bottom Line
```

Insert BEFORE this line:

```markdown
## Why This Matters

@superpowers:context/verification-failure-memories.md

## When to Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction before running commands
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases ("done", "complete", "fixed", "working")
- Paraphrases and synonyms ("looks good", "should be fine", "ready")
- Implications of success ("great progress", "almost there")
- ANY communication suggesting completion or correctness

## Holistic Code Review

For holistic code review of the complete implementation (not per-task, but across the full changeset), delegate to `superpowers:code-reviewer`. This is optional but recommended before transitioning to `/finish`.

```

**Step 3: Verify changes**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep -n "failure-memories\|When to Apply\|code-reviewer" modes/verify.md
```
Expected: Matches for the @mention, the "When to Apply" section, and the code-reviewer reference.

**Step 4: Commit**

```bash
git add modes/verify.md && git commit -m "feat: add failure memories, trigger list, and code-reviewer reference to verify mode"
```

---

### Task 12: Update `modes/execute-plan.md` — Add SDD Walkthrough Reference

**Files:**
- Modify: `modes/execute-plan.md`

Add a reference to the SDD walkthrough skill in the appropriate location.

**Step 1: Read the relevant section**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep -n "Model Selection\|walkthrough\|skill" modes/execute-plan.md
```

**Step 2: Add the SDD walkthrough reference**

Find the "Model Selection Guidance" section (starts around line 122). After the closing line of that section (`Default to \`coding\` when uncertain.`), insert:

```markdown

## SDD Worked Example

For a complete worked example showing the realistic conversational flow of the three-agent pipeline — including spec review failures, DONE_WITH_CONCERNS, code quality fix loops, and NEEDS_CONTEXT — load the walkthrough skill:

```
load_skill(skill_name="sdd-walkthrough")
```

This shows 5 realistic tasks with Amplifier-specific `delegate()` calls, `model_role` parameters, and orchestrator judgment calls.
```

**Step 3: Verify the reference was added**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep -n "sdd-walkthrough\|SDD Worked Example" modes/execute-plan.md
```
Expected: Matches for the section heading and the skill name.

**Step 4: Commit**

```bash
git add modes/execute-plan.md && git commit -m "feat: add SDD walkthrough reference to execute-plan mode"
```

---

### Task 13: Update `modes/finish.md` — Add Code Reviewer Reference

**Files:**
- Modify: `modes/finish.md`

Add a reference to the standalone code-reviewer agent as an optional pre-merge step.

**Step 1: Read the relevant section**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && cat -n modes/finish.md | head -40
```

**Step 2: Add the code-reviewer reference**

Find the "Step 1: Verify Tests" section (line 33). After the test verification step and before "Step 2: Summarize the Work", insert:

```markdown

### Step 1.5: Optional Holistic Code Review

If the implementation hasn't had a holistic code review (e.g., it went through per-task pipeline reviews but no full-changeset review), consider delegating to `superpowers:code-reviewer` before presenting completion options:

```
delegate(
  agent="superpowers:code-reviewer",
  instruction="Review the complete implementation on this branch against the design/plan at [path]. Focus on cross-task integration, architectural coherence, and production readiness.",
  context_depth="recent",
  model_role="critique"
)
```

This is optional — skip if a holistic review was already done in `/verify` mode. The per-task pipeline reviews (spec-reviewer + code-quality-reviewer) may be sufficient for smaller changes.
```

**Step 3: Verify the reference was added**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep -n "code-reviewer\|Holistic Code Review" modes/finish.md
```
Expected: Matches for the section heading and the agent reference.

**Step 4: Commit**

```bash
git add modes/finish.md && git commit -m "feat: add optional holistic code review step to finish mode"
```

---

### Task 14: Update `behaviors/superpowers-methodology.yaml` — Register Code Reviewer Agent

**Files:**
- Modify: `behaviors/superpowers-methodology.yaml`

Two changes: (1) register the new code-reviewer agent, (2) update the bundle description to reflect 6 agents.

**Step 1: Read the current file**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && cat -n behaviors/superpowers-methodology.yaml
```

**Step 2: Add the code-reviewer agent to the agents include list**

Find:
```yaml
agents:
  include:
    - superpowers:implementer
    - superpowers:spec-reviewer
    - superpowers:code-quality-reviewer
    - superpowers:brainstormer
    - superpowers:plan-writer
```

Replace with:
```yaml
agents:
  include:
    - superpowers:implementer
    - superpowers:spec-reviewer
    - superpowers:code-quality-reviewer
    - superpowers:code-reviewer
    - superpowers:brainstormer
    - superpowers:plan-writer
```

**Step 3: Update the description to reflect 6 agents**

Find:
```yaml
    Provides 5 agents:
    - implementer: TDD implementation with tests
    - spec-reviewer: Validates against spec compliance
    - code-quality-reviewer: Code quality and best practices
    - brainstormer: Design refinement facilitation
    - plan-writer: Detailed implementation plans
```

Replace with:
```yaml
    Provides 6 agents:
    - implementer: TDD implementation with tests
    - spec-reviewer: Validates against spec compliance
    - code-quality-reviewer: Code quality and best practices
    - code-reviewer: Holistic code review across full changesets
    - brainstormer: Design refinement facilitation
    - plan-writer: Detailed implementation plans
```

**Step 4: Verify changes**

Run:
```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers && grep "code-reviewer\|6 agents" behaviors/superpowers-methodology.yaml
```
Expected: Matches for `superpowers:code-reviewer` in the agents list and `6 agents` in the description.

**Step 5: Commit**

```bash
git add behaviors/superpowers-methodology.yaml && git commit -m "feat: register code-reviewer agent in behavior YAML"
```

---

## Final Verification

After all 14 tasks are complete, run this checklist:

```bash
cd /home/bkrabach/dev/superpowers-loop/amplifier-bundle-superpowers

# Phase 1: New files exist
echo "=== Phase 1: New Files ==="
ls scripts/server.cjs scripts/start-server.sh scripts/stop-server.sh scripts/frame-template.html scripts/helper.js
ls context/visual-companion-guide.md context/spec-document-review-prompt.md context/verification-failure-memories.md
ls agents/code-reviewer.md
ls skills/sdd-walkthrough/SKILL.md skills/sdd-walkthrough/five-task-example.md

# Phase 2: Modifications present
echo "=== Phase 2: Modifications ==="
grep "NO PRODUCTION CODE" context/tdd-depth.md && echo "✓ Iron Law"
grep "TDD Red Flags" context/tdd-depth.md && echo "✓ Red Flags"
grep "Bug Fix Worked Example" context/tdd-depth.md && echo "✓ Bug Fix Example"
grep "dogmatic" context/philosophy.md && echo "✓ New rationalization rows"
grep "Phase 1.5" modes/brainstorm.md && echo "✓ Visual companion phase"
grep "Phase 6" modes/brainstorm.md && echo "✓ Spec self-review phase"
grep "Phase 7" modes/brainstorm.md && echo "✓ User review gate"
grep "visual-companion-guide" agents/brainstormer.md && echo "✓ Brainstormer @mentions"
grep "tool-bash" agents/brainstormer.md && echo "✓ Brainstormer bash tool"
grep "failure-memories" modes/verify.md && echo "✓ Verify failure memories"
grep "When to Apply" modes/verify.md && echo "✓ Verify trigger list"
grep "sdd-walkthrough" modes/execute-plan.md && echo "✓ Execute-plan walkthrough ref"
grep "code-reviewer" modes/finish.md && echo "✓ Finish code-reviewer ref"
grep "superpowers:code-reviewer" behaviors/superpowers-methodology.yaml && echo "✓ YAML agent registration"

# Commit log
echo "=== Commits ==="
git log --oneline -14
```

Expected: All files exist, all grep matches succeed, 14 commits shown (one per task).
