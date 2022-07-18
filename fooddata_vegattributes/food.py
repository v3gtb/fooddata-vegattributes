from dataclasses import dataclass
from typing import cast, Optional, Tuple

from .fooddata import FoodDataDict, SrLegacyFoodDataDict, SurveyFoodDataDict


@dataclass(frozen=True)
class InputFoodStub:
  fdc_id: int  # FIXME wrong, it's a completely unrelated ID => remove later
  description: str
  ingredient_code: int

@dataclass(frozen=True)
class Food:
  description: str
  fdc_id: int

  input_food_stubs: Tuple[InputFoodStub, ...]

  fdc_category_description: str
  """
  Not to be confused with "category" in our sense (vegan/vegetarian/omni)!
  """

  # different numbers identifying foods across FDC dataset releases
  food_code: Optional[int] = None
  'Identifies foods in the FNDDS ("Survey") dataset'

  ndb_number: Optional[int] = None
  "Identifies foods in the SR Legacy dataset"

  @property
  def ingredient_code(self) -> int:
    """
    ID that is most likely to be used to refer to this food as an ingredient.

    Not actually present under this name on the original data; we just take the
    FoodCode for entries in FNDDS ("Survey") and NDB Number for entries in SR
    Legacy.
    """
    return self.food_code if self.food_code is not None else self.ndb_number

  @classmethod
  def from_fdc_food_dict(cls, d: FoodDataDict) -> "Food":
    # TODO not good, use different methods for different datasets or sth.,
    # but that requires effort elsewhere...
    if "foodCode" in d:
      return cls.from_fdc_survey_food_dict(cast(SurveyFoodDataDict, d))
    elif "ndbNumber" in d:
      return cls.from_fdc_sr_legacy_food_dict(cast(SrLegacyFoodDataDict, d))
    else:
      raise ValueError(
        "invalid food data dict with neither foodCode nor ndbNumber"
      )

  @classmethod
  def from_fdc_survey_food_dict(cls, d: SurveyFoodDataDict) -> "Food":
    return cls(
      **cls._kwargs_from_fdc_common_food_dict(d),
      food_code=d["foodCode"],
      fdc_category_description=(
        d["wweiaFoodCategory"]["wweiaFoodCategoryDescription"]
      ),
    )

  @classmethod
  def from_fdc_sr_legacy_food_dict(cls, d: SrLegacyFoodDataDict) -> "Food":
    return cls(
      **cls._kwargs_from_fdc_common_food_dict(d),
      ndb_number=d["ndbNumber"],
      fdc_category_description=d["foodCategory"]["description"],
    )

  @classmethod
  def _kwargs_from_fdc_common_food_dict(cls, d: FoodDataDict) -> dict:
    return dict(
      description=d["description"],
      fdc_id=d["fdcId"],
      input_food_stubs=tuple(
        InputFoodStub(
          x["id"],
          x["foodDescription"],
          x["ingredientCode"],
        ) for x in d["inputFoods"]
      ),
    )
