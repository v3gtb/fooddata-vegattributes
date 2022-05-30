from collections import ChainMap
from pathlib import Path
from unittest.mock import patch

from fooddata_vegattributes.app.annotate_reference_samples import main
from fooddata_vegattributes.reference_samples_csv import ReferenceSamplesCsv

from .conftest import FakeFoodDataJson


def test_annotate_reference_samples(
  fake_fooddata_json: FakeFoodDataJson,
  fake_reference_samples_csv_no_description: Path,
  tmp_path: Path,
):
  # shortcuts
  json_path = fake_fooddata_json.path
  csv_path = fake_reference_samples_csv_no_description.path
  fooddata_dict = fake_fooddata_json.food_data_dicts[0]
  original_ref_sample_dict = (
    fake_reference_samples_csv_no_description.reference_sample_dicts[0]
  )

  # patches
  with patch(
    "fooddata_vegattributes.app.default_paths.default_dir_paths"
    ".survey_fooddata_json",
    json_path,
  ), patch(
    "fooddata_vegattributes.app.default_paths.default_dir_paths"
    ".reference_samples_csv",
    csv_path,
  ), patch(
    "fooddata_vegattributes.app.default_paths.default_dir_paths"
    ".compressed_indexed_fooddata_json",
    tmp_path/"compressed_indexed_fooddata.json.tar.xz",
  ):
    # run annotate-ref app
    main()

  # read results (ref. CSV file hopefully annotated with descriptions)
  with ReferenceSamplesCsv.from_path(csv_path) as ref_csv:
    all_ref_sample_dicts = list(ref_csv.read_all_reference_sample_dicts())
  annotated_ref_sample_dict = all_ref_sample_dicts[0]

  # checks
  assert len(all_ref_sample_dicts) == 1
  assert annotated_ref_sample_dict == ChainMap(
    {
      "description": fooddata_dict["description"],
    },
    original_ref_sample_dict
  )
