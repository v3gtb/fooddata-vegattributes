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
    reference_samples_by_fdc_id = (
      reference_sample_store.get_all_mapped_by_fdc_ids()
    )
    foods_by_fdc_id = food_store.get_mapped_by_fdc_ids(
      reference_samples_by_fdc_id.keys()
    )
    reference_sample_store.reference_samples_csv\
    .reset_and_write_reference_sample_dicts(
      {
        "fdc_id": fdc_id,
        "expected_category": reference_sample.expected_category.name,
        "known_failure": reference_sample.known_failure,
        "description": foods_by_fdc_id[fdc_id].description,
      }
      for fdc_id, reference_sample in reference_samples_by_fdc_id.items()
    )
