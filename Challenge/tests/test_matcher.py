import unittest
from tenant_screening.matcher import TenantMatcher
from tenant_screening.ai_helper import AIHelper
from unittest.mock import MagicMock

class TestTenantMatcher(unittest.TestCase):
    
    def setUp(self):
        """Setup test data before each test runs."""
        self.candidate = {
            "first_name": "Juan",
            "last_name": "Perez",
            "birthdate": "1985-06-15",
            "nationality": "Argentina",
            "age": 39
        }

        self.blacklist_data = [
            {
                "first_name": "Juan",
                "last_name": "Perez",
                "birthdate": "1985-06-15",
                "nationality": "Argentina",
                "age": 39,
                "pipeline": {"type": "refinitiv-blacklist"}
            },
            {
                "first_name": "Carlos",
                "last_name": "Garcia",
                "birthdate": "1979-03-22",
                "nationality": "Mexico",
                "age": 45,
                "pipeline": {"type": "refinitiv-blacklist"}
            }
        ]

        self.api_helper = MagicMock()
        self.api_helper.query_chatgpt = MagicMock(return_value=self.blacklist_data)

        self.matcher = TenantMatcher(
            tenant_data=self.candidate,
            blacklist_data=self.blacklist_data,
            api_helper=self.api_helper
        )

    def test_normalize_name(self):
        """Test name normalization method."""
        normalized = self.matcher.normalize_name("José", "de la Cruz")
        self.assertEqual(normalized, "jose cruz")

    def test_calculate_match_score(self):
        """Test the match score calculation."""
        results = self.matcher.calculate_match_score(self.candidate, self.blacklist_data)
        
        for result in results:
            self.assertIn("match_score", result)
            self.assertIn("confidence", result)
            self.assertIn("classification", result)

    def test_classify(self):
        """Test classification pipeline with mocked API."""
        classified_results = self.matcher.classify(self.candidate, self.blacklist_data)
        
        self.api_helper.query_chatgpt.assert_called_once()

        # Validate classification structure
        self.assertTrue(all("classification" in result for result in classified_results))

if __name__ == "__main__":
    unittest.main()
