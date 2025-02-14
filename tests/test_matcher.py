import unittest
from unittest.mock import MagicMock, patch
from tenant_screening.matcher import TenantMatcher
from tenant_screening.ai_helper import AIHelper
from openai import RateLimitError
import httpx  

class TestTenantMatcher(unittest.TestCase):
    def setUp(self):
        """Set up test data and mock AIHelper"""
        self.tenant_data = {"name": "John Doe", "dob": "1985-07-20", "nationality": "USA"}
        self.blacklist_data = [
            {"name": "Jonathan Doe", "dob": "1985-07-20", "nationality": "USA", "pipeline": {"type": "refinitiv-blacklist"}},
            {"name": "Jane Doe", "dob": "1990-05-15", "nationality": "Canada", "pipeline": {"type": "refinitiv-blacklist"}}
        ]
        
        self.mock_api_helper = AIHelper(api_key="fake_api_key")
        self.mock_api_helper.query_chatgpt = MagicMock(side_effect=self.mock_ai_response)

        self.matcher = TenantMatcher(self.tenant_data, self.blacklist_data, self.mock_api_helper, threshold=80)

    def mock_ai_response(self, tenant, record):
        """Mock AI response for testing"""
        if "Jonathan Doe" in record["name"]:
            return {"classification": "Relevant Match", "reasoning": "High similarity in name and DOB match"}
        return {"classification": "Probably Not Relevant", "reasoning": "No strong match"}

    def test_match_score(self):
        """Ensure that similarity scores are calculated correctly."""
        record = {"name": "Jonathan Doe"}
        score = self.matcher.calculate_match_score(record)
        self.assertTrue(score >= 80, f"Expected score >= 80, but got {score}")

    def test_filter_results(self):
        """Test if the filter correctly classifies matches."""
        results = self.matcher.filter_results()
        
        relevant_matches = [r for r in results if r["classification"] == "Relevant Match"]
        self.assertGreater(len(relevant_matches), 0, "Expected at least one Relevant Match")

    def test_ai_classification(self):
        """Test if AI classification is correctly applied."""
        results = self.matcher.filter_results()
        
        for result in results:
            if "Jonathan Doe" in result["name"]:
                self.assertEqual(result["classification"], "Relevant Match")
            else:
                self.assertEqual(result["classification"], "Probably Not Relevant")

    @patch.object(AIHelper, 'query_chatgpt')
    def test_fallback_matching_on_ai_failure(self, mock_query_chatgpt):
        """Test fallback logic when AI API fails."""
    
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429  
        mock_response.request = MagicMock()
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.headers = {"x-request-id": "mock-request-id"}

        mock_query_chatgpt.side_effect = RateLimitError(
            message="API quota exceeded",
            response=mock_response,  
            body=mock_response.json()
        )

        results = self.matcher.filter_results()

        for result in results:
            self.assertIn(result["classification"], ["Relevant Match", "Moderate Match", "Probably Not Relevant"])

if __name__ == "__main__":
    unittest.main()
