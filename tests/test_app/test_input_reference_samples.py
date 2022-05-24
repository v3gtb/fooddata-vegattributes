from pathlib import Path
from unittest.mock import patch

from fooddata_vegattributes.reference_samples_csv import (
  ReferenceSamplesCsv,
  ReferenceSampleDict,
)
from fooddata_vegattributes.app.input_reference_samples import main

from .conftest import FakeFoodDataJson


def test_input_reference_samples(
  fake_fooddata_json: FakeFoodDataJson,
  tmp_path: Path,
):
  # shortcuts
  json_path = fake_fooddata_json.path
  csv_path = tmp_path/"reference_samples.csv"
  fooddata_dict = fake_fooddata_json.food_data_dicts[0]

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
  ), patch(
    "fooddata_vegattributes.app.input_reference_samples.input",
    side_effect=["veg", EOFError("end of stream reached")],
  ):
    # run annotate-ref app
    main()

  # read results (ref. CSV file hopefully annotated with descriptions)
  with ReferenceSamplesCsv.from_path(csv_path) as ref_csv:
    all_ref_sample_dicts = list(ref_csv.read_all_reference_sample_dicts())
  ref_sample_dict: ReferenceSampleDict = all_ref_sample_dicts[0]

  # checks
  assert len(all_ref_sample_dicts) == 1
  assert ref_sample_dict == {
    "fdc_id": fooddata_dict["fdcId"],
    "expected_category": "VEGAN",
    "known_failure": False,
    "description": fooddata_dict["description"],
  }
