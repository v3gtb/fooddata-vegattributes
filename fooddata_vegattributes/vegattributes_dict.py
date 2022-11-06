from collections import ChainMap
from typing import cast, Dict, TypedDict, Union

from .categorization import Categorization
from .food import Food


class VegAttributesBaseDict(TypedDict, total=False):
  fdcId: int
  vegCategory: str
  description: str

class SurveyVegAttributesDict(VegAttributesBaseDict):
  foodCode: int

class SrLegacyVegAttributesDict(VegAttributesBaseDict):
  ndbNumber: int

VegAttributesDict = Union[SurveyVegAttributesDict, SrLegacyVegAttributesDict]

class VerboseVegAttributesDict(VegAttributesBaseDict, total=False):
  vegCategorySource: str
  vegCategoryDiscrepancies: Dict[str, str]
  # ... and also the same foodCode/ndbNumber thing as above but I'm too lazy to
  # create 2 more subclasses... TODO

def appropriate_code_dict_from_food(food: Food) -> Dict[str, int]:
  if food.food_code is not None:
    return { "foodCode": food.food_code }
  elif food.ndb_number is not None:
    return { "ndbNumber": food.ndb_number }
  else:
    raise ValueError("invalid food with neither FoodCode nor NDB Number")

def vegattributes_dict_from_food(
  food: Food,
  categorization: Categorization,
) -> VegAttributesDict:
  return cast(
    VegAttributesDict,
    dict(ChainMap(
      appropriate_code_dict_from_food(food),
      cast(
        dict,
        {
          "fdcId": food.fdc_id,
          "vegCategory": categorization.category.name,
          "description": food.description,
        },
      ),
    ))
  )

def verbose_vegattributes_dict_from_food(
  food: Food,
  categorization: Categorization,
) -> VerboseVegAttributesDict:
  return cast(
    VerboseVegAttributesDict,
    dict(ChainMap(
      appropriate_code_dict_from_food(food),
      {
        "description": food.description,
        "vegCategorySource": categorization.source.name,
        **(
          {
            "vegCategoryDiscrepancies": {
              source.name: category.name
              for source, category in categorization.discrepancies.items()
            }
          } if categorization.discrepancies else {}
        ),
      },
      cast(dict, vegattributes_dict_from_food(food, categorization)),
    ))
  )
