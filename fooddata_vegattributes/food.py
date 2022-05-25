from dataclasses import dataclass

from .fooddata import FoodDataDict


@dataclass(frozen=True)
class Food:
  description: str
  fdc_id: int

  @classmethod
  def from_fdc_food_dict(cls, d: FoodDataDict):
    description = d["description"]
    fdc_id = d["fdcId"]
    return cls(description=description, fdc_id=fdc_id)
