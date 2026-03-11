"""Tests for skill source ordering strategy.

Verifies that our bundle's skills take precedence over obra's skills
by being listed first in the tool-skills config. First-match-wins
priority means our bundle must appear before obra's.
"""

import os

import yaml
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
BEHAVIOR_YAML = os.path.join(REPO_ROOT, "behaviors", "superpowers-methodology.yaml")


class TestSkillSourceOrder:
    """Tests that our bundle's skills are listed before obra's."""

    @pytest.fixture(autouse=True)
    def load_config(self):
        assert os.path.isfile(BEHAVIOR_YAML), f"Behavior YAML not found: {BEHAVIOR_YAML}"
        with open(BEHAVIOR_YAML) as f:
            self.config = yaml.safe_load(f)

    def _get_skills_config(self) -> list:
        """Find the skills list from the tool-skills module config."""
        tools = self.config.get("tools", [])
        assert tools, "Expected a 'tools' section in behavior YAML"

        for tool in tools:
            if tool.get("module") == "tool-skills":
                skills = tool.get("config", {}).get("skills", [])
                assert skills, "Expected 'skills' list in tool-skills config"
                return skills

        pytest.fail("Could not find 'tool-skills' module in tools section")

    def test_our_skills_listed_first(self):
        """Our bundle (microsoft/amplifier-bundle-superpowers) must be listed first.

        First-match-wins priority means our skill sources take precedence over
        obra's when both bundles define a skill with the same name.
        """
        skills_config = self._get_skills_config()

        assert len(skills_config) >= 2, (
            f"Expected at least 2 skill sources, found {len(skills_config)}: {skills_config}"
        )

        assert "microsoft/amplifier-bundle-superpowers" in skills_config[0], (
            f"Expected our bundle (microsoft/amplifier-bundle-superpowers) to be listed first, "
            f"but first entry is: {skills_config[0]}"
        )

        assert "obra/superpowers" in skills_config[1], (
            f"Expected obra/superpowers to be listed second, "
            f"but second entry is: {skills_config[1]}"
        )
