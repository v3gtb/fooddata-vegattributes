import json
from typing import cast, Dict, List, NewType

FoodDataDict = NewType("FoodDataDict", Dict)

def load_survey_fooddata_dicts() -> List[FoodDataDict]:
  with open("FoodData_Central_survey_food_json_2021-10-28.json") as f:
    food_ds = json.load(f)["SurveyFoods"]
  return cast(List[FoodDataDict], food_ds)
