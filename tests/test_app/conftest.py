from dataclasses import dataclass
import json
from pathlib import Path
import pytest
from typing import List

from fooddata_vegattributes.fooddata import FoodDataDict


@dataclass
class FakeFoodDataJson:
  food_data_dicts: List[FoodDataDict]
  path: Path

@pytest.fixture
def fake_fooddata_json(tmp_path: Path):
  json_path = tmp_path/"fake_fooddata.json"
  food_data = [{ "fdcId": 123456, "description": "A fake food, salted" }]

  with json_path.open("w") as f:
    json.dump({ "SurveyFoods": food_data }, f)

  yield FakeFoodDataJson(food_data_dicts=food_data, path=json_path)
