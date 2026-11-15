import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from openai import OpenAIError

from tenant_screening.ai_helper import AIHelper
from tenant_screening.matcher import TenantMatcher


def chat_reply(content=None, refusal=None):
    """Build an object shaped like an OpenAI chat completion response."""
    message = SimpleNamespace(content=content, refusal=refusal)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def record(score, classification="probably not relevant"):
    """A scored blacklist record as TenantMatcher produces it."""
    return {
        "first_name": "Juan C.",
        "last_name": "Rodriguez",
        "birthdate": "1985-06-15",
        "nationality": "Mexican",
        "age": 38,
        "match_score": score,
        "confidence": "Low",
        "classification": classification,
        "classified_by": "rules",
    }


CANDIDATE = {
    "first_name": "Juan Carlos",
    "last_name": "Rodriguez",
    "birthdate": "1985-06-15",
    "nationality": "Mexican",
    "age": 38,
}


class TestAIHelperWithoutKey(unittest.TestCase):

    def test_missing_key_disables_ai_instead_of_failing(self):
        """No API key: the helper is created and results come back unchanged."""
        with patch.dict(os.environ, {}, clear=True):
            helper = AIHelper()

        self.assertIsNone(helper.client)
        results = [record(70)]
        self.assertEqual(helper.query_chatgpt(CANDIDATE, results), [record(70)])

    def test_full_pipeline_runs_on_fuzzy_matching_alone(self):
        """No API key: TenantMatcher still scores and classifies every record."""
        with patch.dict(os.environ, {}, clear=True):
            helper = AIHelper()

        results = [dict(CANDIDATE, first_name="Juan C.", pipeline={"type": "refinitiv-blacklist"})]
        matcher = TenantMatcher(CANDIDATE, results, helper)
        classified = matcher.classify(CANDIDATE, results)

        self.assertTrue(all(r["classified_by"] == "rules" for r in classified))
        self.assertTrue(all("match_score" in r for r in classified))


class TestAIHelperWithModel(unittest.TestCase):

    def setUp(self):
        self.helper = AIHelper(api_key="test-key", model="test-model")
        self.create = MagicMock()
        self.helper.client = MagicMock()
        self.helper.client.chat.completions.create = self.create

    def test_only_ambiguous_scores_are_sent_to_the_model(self):
        self.create.return_value = chat_reply(json.dumps({"classification": "relevant match", "reason": "Same person."}))
        results = [record(95, "relevant match"), record(70), record(40)]

        self.helper.query_chatgpt(CANDIDATE, results)

        self.create.assert_called_once()
        self.assertEqual(self.create.call_args.kwargs["model"], "test-model")

    def test_valid_reply_replaces_rule_classification(self):
        self.create.return_value = chat_reply(json.dumps({"classification": "relevant match", "reason": "Initial matches."}))

        [result] = self.helper.query_chatgpt(CANDIDATE, [record(70)])

        self.assertEqual(result["classification"], "relevant match")
        self.assertEqual(result["classified_by"], "ai")
        self.assertEqual(result["ai_reason"], "Initial matches.")

    def test_api_error_keeps_rule_classification(self):
        self.create.side_effect = OpenAIError("service unavailable")

        [result] = self.helper.query_chatgpt(CANDIDATE, [record(70)])

        self.assertEqual(result["classification"], "probably not relevant")
        self.assertEqual(result["classified_by"], "rules")

    def test_unexpected_label_is_ignored(self):
        self.create.return_value = chat_reply(json.dumps({"classification": "maybe", "reason": "Unsure."}))

        [result] = self.helper.query_chatgpt(CANDIDATE, [record(70)])

        self.assertEqual(result["classification"], "probably not relevant")
        self.assertEqual(result["classified_by"], "rules")

    def test_invalid_json_is_ignored(self):
        self.create.return_value = chat_reply("relevant match")

        [result] = self.helper.query_chatgpt(CANDIDATE, [record(70)])

        self.assertEqual(result["classified_by"], "rules")

    def test_refusal_is_ignored(self):
        self.create.return_value = chat_reply(refusal="I can't help with that.")

        [result] = self.helper.query_chatgpt(CANDIDATE, [record(70)])

        self.assertEqual(result["classified_by"], "rules")


if __name__ == "__main__":
    unittest.main()
