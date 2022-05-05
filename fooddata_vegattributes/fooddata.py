import json
from typing import cast, List, TypedDict

# NOTE that while the TypedDict PEP (PEP-589) and docs both suggest that extra
# keys are not allowed, this is actually contentious because it contradicts
# structural subtyping - refer to the discussion about transitivity in
# https://mail.python.org/archives/list/typing-sig@python.org/thread/66RITIHDQHVTUMJHH2ORSNWZ6DOPM367
# In any event, we want to use this class to refer to dicts that MUST contain
# the specified keys and MAY contain any other extra keys. But to comply with
# the current (inconsistent) definition of TypedDict, we'll just typing.cast()
# back and forth to regular dict where required.
class FoodDataDict(TypedDict):
    fdcId: int
    description: str

def load_survey_fooddata_dicts() -> List[FoodDataDict]:
  with open("FoodData_Central_survey_food_json_2021-10-28.json") as f:
    food_ds = json.load(f)["SurveyFoods"]
  return cast(List[FoodDataDict], food_ds)
