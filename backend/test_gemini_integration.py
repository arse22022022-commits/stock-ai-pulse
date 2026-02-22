import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from services.llm import LLMService

class TestGeminiIntegration(unittest.TestCase):
    def setUp(self):
        # Mock environment variable
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            self.service = LLMService()

    @patch("google.generativeai.GenerativeModel")
    def test_predict_success(self, mock_model_class):
        # Mock the model and its response
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = '[{"date": "2026-02-21", "price": 155.0, "price_low": 150.0, "price_high": 160.0}]'
        mock_model.generate_content.return_value = mock_response
        
        self.service.model = mock_model
        self.service.enabled = True
        
        data = np.array([150.0, 151.0, 152.0])
        last_date = datetime(2026, 2, 20)
        
        result = self.service.predict(data, prediction_length=1, last_date=last_date, last_price=152.0)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["price"], 155.0)
        self.assertEqual(result[0]["type"], "forecast")
        
    def test_fallback_gbm(self):
        # Disable Gemini to force fallback
        self.service.enabled = False
        
        data = np.array([100.0, 101.0, 102.0])
        last_date = datetime(2026, 2, 20)
        
        result = self.service.predict(data, prediction_length=5, last_date=last_date, last_price=102.0)
        
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["type"], "forecast")
        self.assertTrue("price" in result[0])

if __name__ == "__main__":
    unittest.main()
