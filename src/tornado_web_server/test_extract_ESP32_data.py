from typing import Dict
import unittest
from extract_ESP32_data import extract_ESP32_data

class TestExtractEsp32Data(unittest.TestCase):
    """
    The tests below are for the method that extracts data sent by the ESP32
    """

    def test_extract_ESP32_data(self):
        """
        Test that the extract_ESP32_data function can extract data 
        sent by ESP32 
        """
        ESP32_Data = b'{"ds":"4-23-2022","temperature":78}'
        extracted_data = extract_ESP32_data(ESP32_Data)
        self.assertIsInstance(extracted_data,Dict)
    
if __name__ == '__main__':
    unittest.main()