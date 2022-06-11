import json
from typing import Dict 
def extract_ESP32_data(ESP32_data:bytes)->Dict:
    """
    Gets a data encoded in bytes which has a string representation of dictionary
    containing the data from the ESP32. The goal is to extract this data into a 
    dictionary
    """
    return json.loads(ESP32_data.decode('utf-8'))