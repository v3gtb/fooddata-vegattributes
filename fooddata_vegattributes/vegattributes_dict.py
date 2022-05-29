from collections import ChainMap
from typing import cast, TypedDict

from .categorization import Categorization
from .food import Food


class VegAttributesDict(TypedDict):
  fdcId: int
  vegCategory: str

class VerboseVegAttributesDict(VegAttributesDict):
  description: str
  vegCategorySource: str

def vegattributes_dict_from_food(
  food: Food,
  categorization: Categorization,
) -> VegAttributesDict:
  return cast(
    VegAttributesDict,
    {
      "fdcId": food.fdc_id,
      "vegCategory": categorization.category.name,
    },
  )

def verbose_vegattributes_dict_from_food(
  food: Food,
  categorization: Categorization,
) -> VerboseVegAttributesDict:
  return cast(
    VerboseVegAttributesDict,
    dict(ChainMap(
      {
        "description": food.description,
        "vegCategorySource": categorization.source.name
      },
      cast(dict, vegattributes_dict_from_food(food, categorization)),
    ))
  )
