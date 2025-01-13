import pytest
import json

@pytest.fixture
def plantB_day11_json():
    file_path = 'tests/data/_set1_day1_20230509-125420_014_plantB_day11.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data