import json
from os import PathLike
from typing import cast, List, TypedDict, Union

# NOTE that while the TypedDict PEP (PEP-589) and docs both suggest that extra
# keys are not allowed, this is actually contentious because it contradicts
# structural subtyping - refer to the discussion about transitivity in
# https://mail.python.org/archives/list/typing-sig@python.org/thread/66RITIHDQHVTUMJHH2ORSNWZ6DOPM367
# In any event, we want to use this class to refer to dicts that MUST contain
# the specified keys and MAY contain any other extra keys. But to comply with
# the current (inconsistent) definition of TypedDict, we'll just typing.cast()
# back and forth to regular dict where required.
class InputFoodDict(TypedDict):
  id: int
  foodDescription: str
  ingredientCode: int

class FoodDataDict(TypedDict):
  fdcId: int
  description: str
  inputFoods: List[InputFoodDict]

class SurveyFoodDataDict(FoodDataDict):
  foodCode: int
  wweiaFoodCategory: dict

class SrLegacyFoodDataDict(FoodDataDict):
  ndbNumber: int
  foodCategory: dict

def load_survey_fooddata_dicts(
  path: Union[PathLike, str, bytes]
) -> List[SurveyFoodDataDict]:
  with open(path) as f:
    food_ds = json.load(f)["SurveyFoods"]
  return cast(List[SurveyFoodDataDict], food_ds)

def load_sr_legacy_fooddata_dicts(
  path: Union[PathLike, str, bytes]
) -> List[SrLegacyFoodDataDict]:
  with open(path) as f:
    food_ds = json.load(f)["SRLegacyFoods"]
  return cast(List[SrLegacyFoodDataDict], food_ds)
