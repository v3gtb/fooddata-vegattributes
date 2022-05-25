from typing import cast, TypedDict

from .categorization import categorize
from .food import Food


class VegAttributesDict(TypedDict):
  fdcId: int
  vegCategory: str

def vegattributes_dict_from_food(
  food: Food,
  include_description=False
) -> VegAttributesDict:
  return cast(
    VegAttributesDict,
    {
      **({
        "description": food.description
      } if include_description else {} ),
      "fdcId": food.fdc_id,
      "vegCategory": categorize(food).name,
    },
  )
