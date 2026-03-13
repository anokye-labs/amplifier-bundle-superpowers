"""Test that subagent-driven-development.yaml uses per-task sequential pipeline.

The recipe MUST implement: for each task → implement → spec-review loop → quality-review loop.
It must NOT use the batch-all-then-review-all anti-pattern (three separate foreach loops).
"""

import yaml
from pathlib import Path

RECIPES_DIR = Path(__file__).parent.parent / "recipes"
SUBAGENT_RECIPE = RECIPES_DIR / "subagent-driven-development.yaml"
FULL_CYCLE_RECIPE = RECIPES_DIR / "superpowers-full-development-cycle.yaml"
EXECUTING_PLANS_RECIPE = RECIPES_DIR / "executing-plans.yaml"


def load_recipe(path: Path) -> dict:
    """Load and parse a recipe YAML file."""
    content = path.read_text()
    return yaml.safe_load(content)


class TestSubagentRecipeIsValidYAML:
    def test_parses_without_error(self):
        """Recipe must be valid YAML."""
        recipe = load_recipe(SUBAGENT_RECIPE)
        assert recipe is not None
        assert "stages" in recipe

    def test_has_required_top_level_keys(self):
        """Recipe must have name, description, context, stages."""
        recipe = load_recipe(SUBAGENT_RECIPE)
        assert "name" in recipe
        assert "description" in recipe
        assert "context" in recipe
        assert "stages" in recipe

    def test_preserves_plan_path_context(self):
        """Recipe must preserve the plan_path context variable."""
        recipe = load_recipe(SUBAGENT_RECIPE)
        assert "plan_path" in recipe["context"]


class TestSubagentRecipeSingleForeach:
    """The recipe must have exactly ONE foreach over tasks, not three separate ones."""

    def _get_task_execution_stage(self) -> dict:
        recipe = load_recipe(SUBAGENT_RECIPE)
        for stage in recipe["stages"]:
            if stage["name"] == "task-execution":
                return stage
        raise AssertionError("task-execution stage not found")

    def _count_foreach_in_steps(self, steps: list) -> int:
        """Count how many steps at the top level have foreach."""
        return sum(1 for step in steps if "foreach" in step)

    def test_single_foreach_over_tasks(self):
        """There must be exactly ONE foreach at the top level of task-execution steps."""
        stage = self._get_task_execution_stage()
        foreach_count = self._count_foreach_in_steps(stage["steps"])
        assert foreach_count == 1, (
            f"Expected exactly 1 foreach loop, found {foreach_count}. "
            "The recipe must NOT use the batch-all-then-review-all pattern."
        )

    def test_foreach_iterates_over_tasks(self):
        """The single foreach must iterate over {{tasks}}."""
        stage = self._get_task_execution_stage()
        foreach_steps = [s for s in stage["steps"] if "foreach" in s]
        assert len(foreach_steps) == 1
        assert "tasks" in foreach_steps[0]["foreach"], (
            "The foreach must iterate over tasks, not task_implementations or spec_reviews"
        )


class TestSubagentRecipePerTaskPipeline:
    """Within each task iteration, the pipeline must be: implement → spec-review → quality-review."""

    def _get_foreach_step(self) -> dict:
        recipe = load_recipe(SUBAGENT_RECIPE)
        for stage in recipe["stages"]:
            if stage["name"] == "task-execution":
                for step in stage["steps"]:
                    if "foreach" in step:
                        return step
        raise AssertionError("foreach step not found in task-execution stage")

    def _get_nested_steps(self) -> list:
        """Get the steps nested inside the foreach."""
        foreach_step = self._get_foreach_step()
        # The nested steps could be in 'steps' key (for nested step blocks)
        # or the foreach step itself could contain agent/prompt directly
        if "steps" in foreach_step:
            return foreach_step["steps"]
        # If no nested steps, return just the foreach step itself
        return [foreach_step]

    def _find_step_by_agent_pattern(
        self, steps: list, agent_pattern: str
    ) -> dict | None:
        """Find a step (possibly nested) that uses an agent matching the pattern."""
        for step in steps:
            if "agent" in step and agent_pattern in step["agent"]:
                return step
            # Check nested steps (in while loops)
            if "steps" in step:
                found = self._find_step_by_agent_pattern(step["steps"], agent_pattern)
                if found:
                    return found
        return None

    def _find_all_agents_in_order(self, steps: list) -> list[str]:
        """Recursively find all agent references in order."""
        agents = []
        for step in steps:
            if "agent" in step:
                agents.append(step["agent"])
            if "steps" in step:
                agents.extend(self._find_all_agents_in_order(step["steps"]))
        return agents

    def test_has_implementer_step(self):
        """The foreach must contain an implementer step."""
        steps = self._get_nested_steps()
        impl = self._find_step_by_agent_pattern(steps, "implementer")
        assert impl is not None, "No implementer agent found in per-task pipeline"

    def test_has_spec_reviewer_step(self):
        """The foreach must contain a spec-reviewer step."""
        steps = self._get_nested_steps()
        reviewer = self._find_step_by_agent_pattern(steps, "spec-reviewer")
        assert reviewer is not None, "No spec-reviewer agent found in per-task pipeline"

    def test_has_quality_reviewer_step(self):
        """The foreach must contain a code-quality-reviewer step."""
        steps = self._get_nested_steps()
        reviewer = self._find_step_by_agent_pattern(steps, "code-quality-reviewer")
        assert reviewer is not None, (
            "No code-quality-reviewer agent found in per-task pipeline"
        )

    def test_implementer_comes_before_spec_review(self):
        """Implementer must run BEFORE spec review within each task."""
        steps = self._get_nested_steps()
        agents = self._find_all_agents_in_order(steps)
        impl_indices = [i for i, a in enumerate(agents) if "implementer" in a]
        spec_indices = [i for i, a in enumerate(agents) if "spec-reviewer" in a]
        assert impl_indices, "No implementer agent found"
        assert spec_indices, "No spec-reviewer agent found"
        # First implementer must come before first spec-reviewer
        assert impl_indices[0] < spec_indices[0], (
            "Implementer must come BEFORE spec-reviewer in the pipeline"
        )

    def test_spec_review_comes_before_quality_review(self):
        """Spec review must run BEFORE quality review within each task."""
        steps = self._get_nested_steps()
        agents = self._find_all_agents_in_order(steps)
        spec_indices = [i for i, a in enumerate(agents) if "spec-reviewer" in a]
        quality_indices = [
            i for i, a in enumerate(agents) if "code-quality-reviewer" in a
        ]
        assert spec_indices, "No spec-reviewer agent found"
        assert quality_indices, "No code-quality-reviewer agent found"
        # First spec-reviewer must come before first quality-reviewer
        assert spec_indices[0] < quality_indices[0], (
            "Spec-reviewer must come BEFORE code-quality-reviewer in the pipeline"
        )


class TestSubagentRecipeReviewIteration:
    """The recipe must have some form of review iteration (convergence loops)."""

    def _get_foreach_step(self) -> dict:
        recipe = load_recipe(SUBAGENT_RECIPE)
        for stage in recipe["stages"]:
            if stage["name"] == "task-execution":
                for step in stage["steps"]:
                    if "foreach" in step:
                        return step
        raise AssertionError("foreach step not found")

    def _find_review_iteration(self, steps: list) -> bool:
        """Check if any step has review iteration (while_condition, condition, or re-review)."""
        for step in steps:
            # Check for while loops
            if "while_condition" in step:
                return True
            # Check for conditional re-implementation
            if "condition" in step:
                return True
            # Check nested steps
            if "steps" in step:
                if self._find_review_iteration(step["steps"]):
                    return True
        return False

    def test_has_review_iteration_mechanism(self):
        """There must be some form of review iteration within the foreach."""
        foreach_step = self._get_foreach_step()
        steps = foreach_step.get("steps", [foreach_step])
        assert self._find_review_iteration(steps), (
            "No review iteration mechanism found. "
            "Expected while_condition, condition, or re-review pattern."
        )


class TestSubagentRecipePreservesApprovalGates:
    """Existing approval gates must be preserved."""

    def test_has_final_review_stage(self):
        """The final-review stage with approval gate must still exist."""
        recipe = load_recipe(SUBAGENT_RECIPE)
        stage_names = [s["name"] for s in recipe["stages"]]
        assert "final-review" in stage_names, "final-review stage is missing"

    def test_final_review_has_approval(self):
        """The final-review stage must have an approval gate."""
        recipe = load_recipe(SUBAGENT_RECIPE)
        for stage in recipe["stages"]:
            if stage["name"] == "final-review":
                assert "approval" in stage, "final-review stage missing approval gate"
                assert stage["approval"].get("required") is True
                return
        raise AssertionError("final-review stage not found")

    def test_has_finish_stage(self):
        """The finish stage must still exist."""
        recipe = load_recipe(SUBAGENT_RECIPE)
        stage_names = [s["name"] for s in recipe["stages"]]
        assert "finish" in stage_names, "finish stage is missing"


class TestSubagentRecipePreservesContextVariables:
    """Key context variables must be referenced in the recipe."""

    def test_references_plan_path(self):
        """Recipe must reference plan_path."""
        content = SUBAGENT_RECIPE.read_text()
        assert "plan_path" in content

    def test_references_tasks(self):
        """Recipe must reference tasks variable (via dot-notation on plan_data)."""
        content = SUBAGENT_RECIPE.read_text()
        assert "{{plan_data.tasks}}" in content

    def test_uses_collect_for_results(self):
        """Recipe must use collect to gather results."""
        content = SUBAGENT_RECIPE.read_text()
        assert "collect:" in content


class TestFullCycleRecipePerTaskReview:
    """The full-cycle recipe should reference or describe per-task review pipeline."""

    def test_is_valid_yaml(self):
        """Full cycle recipe must be valid YAML."""
        recipe = load_recipe(FULL_CYCLE_RECIPE)
        assert recipe is not None

    def test_execute_plan_uses_sdd_recipe(self):
        """The execute-plan step must use type: recipe referencing subagent-driven-development."""
        recipe = load_recipe(FULL_CYCLE_RECIPE)
        # Find the implementation stage
        for stage in recipe["stages"]:
            if stage["name"] == "implementation":
                # Find execute-plan step
                for step in stage["steps"]:
                    if step.get("id") == "execute-plan":
                        # Must use type: recipe
                        assert step.get("type") == "recipe", (
                            "execute-plan step must have type: recipe, "
                            f"got type: {step.get('type')!r}"
                        )
                        # Must reference subagent-driven-development
                        step_text = str(step)
                        assert "subagent-driven-development" in step_text, (
                            "execute-plan step must reference subagent-driven-development recipe"
                        )
                        return
        raise AssertionError("execute-plan step not found in implementation stage")


class TestExecutingPlansRecipeReview:
    """The executing-plans recipe should include per-task review requirements."""

    def test_is_valid_yaml(self):
        """Executing plans recipe must be valid YAML."""
        recipe = load_recipe(EXECUTING_PLANS_RECIPE)
        assert recipe is not None

    def test_has_per_task_review_instructions(self):
        """The executing-plans recipe must have explicit PER-TASK REVIEW instructions."""
        content = EXECUTING_PLANS_RECIPE.read_text()
        assert "PER-TASK REVIEW" in content, (
            "executing-plans.yaml must include a 'PER-TASK REVIEW' section "
            "with spec check, quality check, and test verification requirements"
        )


EXPECTED_RETRY = {
    "max_attempts": 3,
    "backoff": "exponential",
    "initial_delay": 5,
    "max_delay": 120,
}


class TestSubagentRecipeAPIResilience:
    """SDD recipe must have retry blocks and resilience config on vulnerable agent steps."""

    def _load(self) -> dict:
        return load_recipe(SUBAGENT_RECIPE)

    def _find_step_by_id(self, steps: list, step_id: str) -> dict | None:
        """Recursively find a step by its id field."""
        for step in steps:
            if step.get("id") == step_id:
                return step
            for sub_key in ("steps",):
                if sub_key in step:
                    found = self._find_step_by_id(step[sub_key], step_id)
                    if found:
                        return found
        return None

    def _find_step_in_recipe(self, step_id: str) -> dict:
        """Find a step by id anywhere in the recipe stages."""
        recipe = self._load()
        for stage in recipe["stages"]:
            found = self._find_step_by_id(stage.get("steps", []), step_id)
            if found:
                return found
        raise AssertionError(f"Step '{step_id}' not found anywhere in recipe")

    def _assert_has_retry(self, step: dict, step_id: str) -> None:
        assert "retry" in step, (
            f"Step '{step_id}' is missing a retry block. "
            "API-vulnerable steps must have retry configuration."
        )
        retry = step["retry"]
        assert retry.get("max_attempts") == EXPECTED_RETRY["max_attempts"], (
            f"Step '{step_id}' retry.max_attempts must be {EXPECTED_RETRY['max_attempts']}, "
            f"got {retry.get('max_attempts')!r}"
        )
        assert retry.get("backoff") == EXPECTED_RETRY["backoff"], (
            f"Step '{step_id}' retry.backoff must be '{EXPECTED_RETRY['backoff']}', "
            f"got {retry.get('backoff')!r}"
        )
        assert retry.get("initial_delay") == EXPECTED_RETRY["initial_delay"], (
            f"Step '{step_id}' retry.initial_delay must be {EXPECTED_RETRY['initial_delay']}, "
            f"got {retry.get('initial_delay')!r}"
        )
        assert retry.get("max_delay") == EXPECTED_RETRY["max_delay"], (
            f"Step '{step_id}' retry.max_delay must be {EXPECTED_RETRY['max_delay']}, "
            f"got {retry.get('max_delay')!r}"
        )

    # --- retry block tests ---

    def test_implement_step_has_retry(self):
        """The 'implement' step must have a retry block."""
        step = self._find_step_in_recipe("implement")
        self._assert_has_retry(step, "implement")

    def test_spec_review_step_has_retry(self):
        """The 'spec-review' step must have a retry block."""
        step = self._find_step_in_recipe("spec-review")
        self._assert_has_retry(step, "spec-review")

    def test_spec_fix_step_has_retry(self):
        """The 'spec-fix' step must have a retry block."""
        step = self._find_step_in_recipe("spec-fix")
        self._assert_has_retry(step, "spec-fix")

    def test_quality_review_step_has_retry(self):
        """The 'quality-review' step must have a retry block."""
        step = self._find_step_in_recipe("quality-review")
        self._assert_has_retry(step, "quality-review")

    def test_quality_fix_step_has_retry(self):
        """The 'quality-fix' step must have a retry block."""
        step = self._find_step_in_recipe("quality-fix")
        self._assert_has_retry(step, "quality-fix")

    def test_full_code_review_step_has_retry(self):
        """The 'full-code-review' step must have a retry block."""
        step = self._find_step_in_recipe("full-code-review")
        self._assert_has_retry(step, "full-code-review")

    # --- timeout tests ---

    def test_implement_step_timeout_is_1200(self):
        """The 'implement' step timeout must be 1200 (bumped from 900 for API load)."""
        step = self._find_step_in_recipe("implement")
        assert step.get("timeout") == 1200, (
            f"Step 'implement' timeout must be 1200, got {step.get('timeout')!r}. "
            "900s was too tight under API load."
        )

    def test_load_plan_step_timeout_is_600(self):
        """The 'load-plan' step timeout must be 600 (bumped from 300 for large plans)."""
        step = self._find_step_in_recipe("load-plan")
        assert step.get("timeout") == 600, (
            f"Step 'load-plan' timeout must be 600, got {step.get('timeout')!r}. "
            "300s was too tight for large plans with 15+ tasks."
        )

    # --- on_error tests ---

    def test_task_summary_has_on_error_continue(self):
        """The 'task-summary' step must have on_error: continue."""
        step = self._find_step_in_recipe("task-summary")
        assert step.get("on_error") == "continue", (
            f"Step 'task-summary' must have on_error: continue, "
            f"got {step.get('on_error')!r}. "
            "Non-critical summary steps must not fail the whole recipe."
        )

    def test_prepare_approval_has_on_error_continue(self):
        """The 'prepare-approval' step must have on_error: continue."""
        step = self._find_step_in_recipe("prepare-approval")
        assert step.get("on_error") == "continue", (
            f"Step 'prepare-approval' must have on_error: continue, "
            f"got {step.get('on_error')!r}. "
            "Non-critical prep steps must not fail the whole recipe."
        )
