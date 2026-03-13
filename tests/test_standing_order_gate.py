"""Test that the standing order includes a step 0 check for active modes."""

from pathlib import Path

INSTRUCTIONS = Path(__file__).parent.parent / "context" / "instructions.md"


def read_instructions() -> str:
    return INSTRUCTIONS.read_text(encoding="utf-8")


def get_standing_order() -> str:
    content = read_instructions()
    start = content.index("<STANDING-ORDER>")
    end = content.index("</STANDING-ORDER>")
    return content[start:end]


class TestStandingOrderGate:
    """Fix 4: Standing order must check if a mode is already active."""

    def test_has_step_zero(self) -> None:
        standing_order = get_standing_order()
        assert "0." in standing_order, "STANDING-ORDER must have a step 0"

    def test_step_zero_mentions_mode_active(self) -> None:
        standing_order = get_standing_order()
        assert "MODE ACTIVE" in standing_order

    def test_step_zero_says_do_not_reactivate(self) -> None:
        standing_order = get_standing_order().lower()
        assert "re-activate" in standing_order or "already active" in standing_order

    def test_original_steps_still_present(self) -> None:
        standing_order = get_standing_order()
        for step in ["1.", "2.", "3.", "4."]:
            assert step in standing_order, f"Step {step} must still be present"


class TestStandingOrderModeActivation:
    """Fix 3: Standing order must explicitly instruct mode activation via tool on consent."""

    def test_has_step_five(self) -> None:
        standing_order = get_standing_order()
        assert "5." in standing_order, (
            "STANDING-ORDER must have a step 5 for mode activation"
        )

    def test_step_five_requires_mode_tool_call(self) -> None:
        """Step 5 must instruct the agent to call the mode tool, not just describe the mode."""
        standing_order = get_standing_order().lower()
        # Must reference the mode tool call mechanism
        assert "mode(" in standing_order or "mode tool" in standing_order, (
            "STANDING-ORDER step 5 must reference calling the mode() tool"
        )

    def test_step_five_mentions_consent(self) -> None:
        """Step 5 must be triggered by user consent."""
        standing_order = get_standing_order().lower()
        assert "consent" in standing_order or "consents" in standing_order, (
            "STANDING-ORDER step 5 must mention user consent as the trigger"
        )

    def test_step_five_forbids_conversational_description(self) -> None:
        """Step 5 must explicitly say NOT to just describe the mode conversationally."""
        standing_order = get_standing_order().lower()
        assert "do not" in standing_order or "don't" in standing_order, (
            "STANDING-ORDER step 5 must warn against merely describing the mode conversationally"
        )

    def test_step_five_mentions_slash_command_as_implicit_consent(self) -> None:
        """Slash commands like /brainstorm must be recognized as implicit consent."""
        standing_order = get_standing_order()
        # Check for slash command examples
        assert (
            "/brainstorm" in standing_order or "slash command" in standing_order.lower()
        ), "STANDING-ORDER step 5 must mention slash commands as implicit consent"
