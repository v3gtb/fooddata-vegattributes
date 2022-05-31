from dataclasses import dataclass
from typing import Tuple

from .fooddata import FoodDataDict


@dataclass(frozen=True)
class InputFoodStub:
  fdc_id: int
  description: str

@dataclass(frozen=True)
class Food:
  description: str
  fdc_id: int
  input_food_stubs: Tuple[InputFoodStub, ...]

  @classmethod
  def from_fdc_food_dict(cls, d: FoodDataDict):
    return cls(
      description=d["description"],
      fdc_id=d["fdcId"],
      input_food_stubs=tuple(
        InputFoodStub(x["id"], x["foodDescription"]) for x in d["inputFoods"]
      ),
    )
