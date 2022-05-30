from ..auto_indexed_fooddata_food_store import (
  auto_compressed_indexed_fooddata_food_store
)
from ..csv_reference_sample_store import CsvReferenceSampleStore

from .default_paths import default_dir_paths


def main():
  with auto_compressed_indexed_fooddata_food_store(
    compressed_indexed_json_path=(
      default_dir_paths.compressed_indexed_fooddata_json
    ),
    fooddata_json_path=default_dir_paths.survey_fooddata_json,
  ) as food_store, (
    CsvReferenceSampleStore.from_path_and_food_store(
      default_dir_paths.reference_samples_csv,
      food_store=food_store,
    )
  ) as reference_sample_store:
    # simply read them out and write them back, the store automatically
    # annotates with descriptions on write
    reference_samples = list(reference_sample_store.iter_all())
    reference_sample_store.reset_and_put_all(reference_samples)
