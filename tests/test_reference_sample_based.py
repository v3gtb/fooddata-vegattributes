import pytest

from fooddata_vegattributes.csv_reference_sample_store import (
  CsvReferenceSampleStore
)
from fooddata_vegattributes.indexed_fooddata_food_store import (
  IndexedFoodDataFoodStore
)

def pytest_generate_tests(metafunc):
  with IndexedFoodDataFoodStore.from_path(
    "indexed_FoodData_Central_survey_food_json_2021-10-28.jsons.tar.xz"
  ) as food_store, (
    CsvReferenceSampleStore.from_path_and_food_store(
      "reference_samples.csv",
      food_store
    )
  ) as reference_sample_store:
    reference_samples = reference_sample_store.get_all()
    if "reference_sample" in metafunc.fixturenames:
      metafunc.parametrize(
        "reference_sample",
        [
          pytest.param(
            reference_sample,
            marks=(
              [pytest.mark.xfail(strict=True)]
              if reference_sample.known_failure
              else []
            )
          )
          for reference_sample in reference_samples
        ],
        ids=lambda s: (
          f"{s.food.fdc_id}_"
          f"{s.food.description.replace(' ', '_').replace(',', '')}"
        )
      )

def test_categorization(reference_sample):
  category = reference_sample.food.category
  expected_category = reference_sample.expected_category
  assert category == expected_category
