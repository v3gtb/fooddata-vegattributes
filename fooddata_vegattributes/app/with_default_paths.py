from contextlib import contextmanager

from ..auto_indexed_fooddata_food_store import (
  auto_compressed_indexed_fooddata_food_store
)
from ..csv_reference_sample_store import CsvReferenceSampleStore

from .default_paths import default_dir_paths


@contextmanager
def default_food_and_reference_sample_stores(create_ref_store: bool=False):
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
      create=create_ref_store,
    )
  ) as reference_sample_store:
    yield (food_store, reference_sample_store)
