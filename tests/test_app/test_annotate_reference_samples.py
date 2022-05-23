from collections import ChainMap
from dataclasses import dataclass
from pathlib import Path
import pytest
from unittest.mock import patch
from typing import List

from fooddata_vegattributes.reference_samples_csv import (
  ReferenceSamplesCsv,
  ReferenceSampleDict,
)
from fooddata_vegattributes.app.annotate_reference_samples import main

from .conftest import FakeFoodDataJson


@dataclass
class FakeReferenceSampleCsv:
  reference_sample_dicts: List[ReferenceSampleDict]
  path: Path

@pytest.fixture
def fake_reference_samples_csv_no_description(
  fake_fooddata_json: FakeFoodDataJson,
  tmp_path: Path,
):
  reference_sample_dicts = [
    dict(
      fdc_id=food_data_dict["fdcId"],
      expected_category="VEGAN",
      known_failure=False,
      description=None
    )
    for food_data_dict in fake_fooddata_json.food_data_dicts
  ]
  csv_path = tmp_path/"reference_samples.csv"
  with ReferenceSamplesCsv.from_path(csv_path, "w") as ref_csv:
    ref_csv.reset_and_write_reference_sample_dicts(reference_sample_dicts)
  yield FakeReferenceSampleCsv(
    reference_sample_dicts=reference_sample_dicts,
    path=csv_path,
  )

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
