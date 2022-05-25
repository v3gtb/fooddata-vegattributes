import pytest

from fooddata_vegattributes.auto_indexed_fooddata_food_store import (
  auto_compressed_indexed_fooddata_food_store
)
from fooddata_vegattributes.categorization import categorize
from fooddata_vegattributes.csv_reference_sample_store import (
  CsvReferenceSampleStore
)
from fooddata_vegattributes.app.default_paths import default_dir_paths


def pytest_generate_tests(metafunc):
  with auto_compressed_indexed_fooddata_food_store(
    compressed_indexed_json_path=(
      default_dir_paths.compressed_indexed_fooddata_json
    ),
    fooddata_json_path=default_dir_paths.survey_fooddata_json
  ) as food_store, (
    CsvReferenceSampleStore.from_path_and_food_store(
      default_dir_paths.reference_samples_csv,
      food_store,
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
  category = categorize(reference_sample.food)
  expected_category = reference_sample.expected_category
  assert category == expected_category
