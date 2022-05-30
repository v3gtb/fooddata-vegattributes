from collections import ChainMap
from typing import cast, Dict, TypedDict

from .categorization import Categorization
from .food import Food


class VegAttributesDict(TypedDict):
  fdcId: int
  vegCategory: str

class VerboseVegAttributesDict(VegAttributesDict, total=False):
  description: str
  vegCategorySource: str
  vegCategoryDiscrepancies: Dict[str, str]

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
