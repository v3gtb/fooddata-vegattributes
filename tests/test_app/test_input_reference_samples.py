from dataclasses import dataclass
from pathlib import Path
import pytest
from typing import Any
from unittest.mock import patch

from fooddata_vegattributes.io.reference_samples_csv import (
  ReferenceSamplesCsv,
  ReferenceSampleDict,
)
from fooddata_vegattributes.app.input_reference_samples import main

from .conftest import FakeFoodDataJson


@dataclass
class PatchedPaths:
  fake_fooddata_json: FakeFoodDataJson
  csv_path: Path

@pytest.fixture
def patched_paths(fake_fooddata_json: FakeFoodDataJson, tmp_path: Path):
  csv_path = tmp_path/"reference_samples.csv"
  json_path = fake_fooddata_json.path
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
    yield PatchedPaths(
      fake_fooddata_json=fake_fooddata_json,
      csv_path=csv_path
    )

def test_input_reference_samples(
  patched_paths: PatchedPaths,
  tmp_path: Path,
):
  # shortcuts
  csv_path = patched_paths.csv_path
  fooddata_dict = patched_paths.fake_fooddata_json.food_data_dicts[0]

  # patches
  with patch(
    "fooddata_vegattributes.app.input_reference_samples.input",
    side_effect=["s", "veg", EOFError("end of stream reached")],
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


@pytest.mark.parametrize("quit_via_input", ["q", EOFError("end of stream")])
def test_input_reference_samples_quit(
  quit_via_input: Any,
  patched_paths: PatchedPaths,
  tmp_path: Path,
):
  # shortcuts
  csv_path = patched_paths.csv_path

  # patches
  with patch(
    "fooddata_vegattributes.app.input_reference_samples.input",
    side_effect=["s", quit_via_input],
  ):
    # run annotate-ref app
    main()

  # read results (ref. CSV file hopefully annotated with descriptions)
  with ReferenceSamplesCsv.from_path(csv_path) as ref_csv:
    all_ref_sample_dicts = list(ref_csv.read_all_reference_sample_dicts())

  # check
  assert len(all_ref_sample_dicts) == 0
