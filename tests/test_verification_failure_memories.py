"""Tests for context/verification-failure-memories.md.

Verifies that the verification failure memories document exists with all required content:
- 5 specific incidents
- Pattern section
- Closing quote about honesty/replacement
- ~30-35 lines
"""

from pathlib import Path

CONTEXT_DIR = Path(__file__).parent.parent / "context"
MEMORIES_FILE = CONTEXT_DIR / "verification-failure-memories.md"


def read_content() -> str:
    assert MEMORIES_FILE.is_file(), f"File does not exist: {MEMORIES_FILE}"
    return MEMORIES_FILE.read_text()


class TestFileExists:
    def test_file_exists(self):
        assert MEMORIES_FILE.is_file(), (
            "context/verification-failure-memories.md must exist"
        )


class TestFiveIncidents:
    def test_incident_1_false_completion_trust(self):
        content = read_content()
        assert "I don't believe you" in content, (
            "Must contain incident 1: 'I don't believe you' trust breakdown"
        )

    def test_incident_2_undefined_functions(self):
        content = read_content()
        assert (
            "undefined" in content.lower()
            or "runtime crash" in content.lower()
            or "never written" in content.lower()
        ), "Must contain incident 2: undefined functions / runtime crash"

    def test_incident_3_missing_requirements(self):
        content = read_content()
        assert (
            "5 of 8" in content or "5/8" in content or "missing" in content.lower()
        ), "Must contain incident 3: missing requirements discovered post-merge"

    def test_incident_4_hours_wasted_false_completion(self):
        content = read_content()
        assert "Done!" in content or "doesn't work" in content or "2-hour" in content, (
            "Must contain incident 4: hours wasted on false completion"
        )

    def test_incident_5_silent_regression(self):
        content = read_content()
        assert (
            "regression" in content.lower() or "full test suite" in content.lower()
        ), "Must contain incident 5: silent regression"


class TestPatternSection:
    def test_has_pattern_section(self):
        content = read_content()
        assert "Pattern" in content or "pattern" in content.lower(), (
            "Must contain a Pattern section"
        )

    def test_pattern_mentions_root_cause(self):
        content = read_content()
        assert "root cause" in content.lower() or "same root" in content.lower(), (
            "Pattern section must identify the root cause"
        )

    def test_pattern_mentions_verification_vs_hope(self):
        content = read_content()
        assert "hope" in content.lower() or "engineering" in content.lower(), (
            "Pattern section must contrast verification/engineering vs hope"
        )


class TestClosingQuote:
    def test_closing_mentions_honesty(self):
        content = read_content()
        assert "Honesty" in content or "honesty" in content.lower(), (
            "Closing must reference honesty as a core value"
        )

    def test_closing_mentions_replacement(self):
        content = read_content()
        assert "replaced" in content.lower() or "replace" in content.lower(), (
            "Closing must mention replacement as consequence of lying"
        )

    def test_closing_mentions_lie(self):
        content = read_content()
        assert "lie" in content.lower() or "lie," in content.lower(), (
            "Closing must include 'if you lie' warning"
        )


class TestApproximateLength:
    def test_is_approximately_30_to_35_lines(self):
        content = read_content()
        lines = content.splitlines()  # total lines including blank ones
        # The spec says ~30-35 lines total. Allow some flexibility: 25-45 lines.
        assert 25 <= len(lines) <= 45, (
            f"File should be ~30-35 total lines, got {len(lines)}"
        )
