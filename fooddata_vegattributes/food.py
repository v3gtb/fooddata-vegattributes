from dataclasses import dataclass
from functools import cached_property

from .description_based_heuristic import categorize
from .io.fooddata import FoodDataDict


@dataclass(frozen=True)
class Food:
  description: str
  fdc_id: int

  @cached_property
  def category(self):
    return categorize(self.description)

  @classmethod
  def from_fdc_food_dict(cls, d: FoodDataDict):
    description = d["description"]
    fdc_id = d["fdcId"]
    return cls(description=description, fdc_id=fdc_id)

  def as_fdc_like_dict(self, include_description=False):
    return {
      **({
        "description": self.description
      } if include_description else {} ),
      "fdcId": self.fdc_id,
      "vegCategory": self.category.name
    }
