from typing import cast, TypedDict

from .category import Category
from .food import Food


class VegAttributesDict(TypedDict):
  fdcId: int
  vegCategory: str

def vegattributes_dict_from_food(
  food: Food,
  category: Category,
  include_description=False
) -> VegAttributesDict:
  return cast(
    VegAttributesDict,
    {
      **({
        "description": food.description
      } if include_description else {} ),
      "fdcId": food.fdc_id,
      "vegCategory": category.name,
    },
  )
