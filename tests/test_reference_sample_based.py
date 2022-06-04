import pytest

from fooddata_vegattributes.app.with_default_paths import (
  default_food_and_reference_sample_stores
)
from fooddata_vegattributes import combined_heuristic
from fooddata_vegattributes.categorization import Categorizer
from fooddata_vegattributes.food import Food
from fooddata_vegattributes.reference_sample import ReferenceSample


def suitable_name(s: str):
  replace_with_underscore = " ,.-;:/"
  for r in replace_with_underscore:
    s = s.replace(r, "_")
  while "__" in s:
    s = s.replace("__", "_")
  return s

def pytest_generate_tests(metafunc):
  with default_food_and_reference_sample_stores() as (
    food_store, reference_sample_store
  ):
    reference_samples_by_fdc_id = (
      reference_sample_store.get_all_mapped_by_fdc_ids()
    )
    foods_by_fdc_id = food_store.get_mapped_by_fdc_ids(
      reference_samples_by_fdc_id.keys()
    )
    reference_samples_and_foods = [
      (reference_sample, foods_by_fdc_id[fdc_id])
      for fdc_id, reference_sample in reference_samples_by_fdc_id.items()
    ]
  if all(x in metafunc.fixturenames for x in ["reference_sample", "food"]):
    metafunc.parametrize(
      ("reference_sample", "food"),
      [
        pytest.param(
          reference_sample,
          food,
          marks=(
            [pytest.mark.xfail(strict=True)]
            if reference_sample.known_failure
            else []
          ),
        )
        for reference_sample, food in reference_samples_and_foods
      ],
      ids=[
        f"{reference_sample.fdc_id}-{suitable_name(food.description)}"
        for reference_sample, food in reference_samples_and_foods
      ]
    )

def test_combined_heuristic(
  reference_sample: ReferenceSample, food: Food
):
  with default_food_and_reference_sample_stores() as (
    food_store, reference_sample_store
  ):
    categorizer = Categorizer(
      food_store=food_store,
      reference_sample_store=reference_sample_store
    )
    category = combined_heuristic.categorize(
      food, categorizer=categorizer, food_store=food_store
    )
  expected_category = reference_sample.expected_category
  assert category == expected_category
