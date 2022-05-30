import pytest

from fooddata_vegattributes.app.default_paths import default_dir_paths
from fooddata_vegattributes.auto_indexed_fooddata_food_store import (
  auto_compressed_indexed_fooddata_food_store
)
from fooddata_vegattributes.csv_reference_sample_store import (
  CsvReferenceSampleStore
)
from fooddata_vegattributes.description_based_heuristic import categorize
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
  with auto_compressed_indexed_fooddata_food_store(
    compressed_indexed_json_path=(
      default_dir_paths.compressed_indexed_fooddata_json
    ),
    survey_fooddata_json_path=default_dir_paths.survey_fooddata_json,
    sr_legacy_fooddata_json_path=default_dir_paths.sr_legacy_fooddata_json,
  ) as food_store, (
    CsvReferenceSampleStore.from_path_and_food_store(
      default_dir_paths.reference_samples_csv,
      food_store,
    )
  ) as reference_sample_store:
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

def test_categorization(reference_sample: ReferenceSample, food: Food):
  category = categorize(food.description)
  expected_category = reference_sample.expected_category
  assert category == expected_category
