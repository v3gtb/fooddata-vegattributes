import json
from pathlib import Path
import pytest
from typing import List
from unittest.mock import patch

from fooddata_vegattributes.app.generate import main
from fooddata_vegattributes.fooddata import FoodDataDict

from .conftest import FakeFoodDataJsons, FakeReferenceSampleCsv


@pytest.fixture
def fake_food_data() -> List[FoodDataDict]:
  return [
    {"fdcId": 123456, "description": "Some food, unsalted"},
    {"fdcId": 654321, "description": "Some m e a t y food, salted"},
  ]

@pytest.fixture
def fake_reference_sample_dicts():
  return [
    dict(
      fdc_id=654321,
      expected_category="OMNI",
      known_failure=False,
      description=None
    ),
  ]

def test_generate_vegattributes_json(
  fake_fooddata_jsons: FakeFoodDataJsons,
  fake_reference_samples_csv: FakeReferenceSampleCsv,
  tmp_path: Path,
):
  # shortcuts
  survey_json_path = fake_fooddata_jsons.survey.path
  sr_legacy_json_path = fake_fooddata_jsons.sr_legacy.path

  # patches
  with patch(
    "fooddata_vegattributes.app.default_paths.default_dir_paths"
    ".survey_fooddata_json",
    survey_json_path,
  ), patch(
    "fooddata_vegattributes.app.default_paths.default_dir_paths"
    ".sr_legacy_fooddata_json",
    sr_legacy_json_path,
  ), patch(
    "fooddata_vegattributes.app.default_paths.default_dir_paths"
    ".compressed_indexed_fooddata_json",
    tmp_path/"compressed_indexed_fooddata.json.tar.xz",
  ), patch(
    "fooddata_vegattributes.app.default_paths.default_dir_paths"
    ".reference_samples_csv",
    tmp_path/"reference_samples.csv",
  ), patch(
    "fooddata_vegattributes.app.default_paths.default_dir_paths"
    ".generated_vegattributes_json",
    tmp_path/"generated_vegattributes.json",
  ) as generated_vegattributes_json_path:
    # run generate app
    main()

  # read results (generated VegAttributes JSON file)
  with generated_vegattributes_json_path.open() as f:
    generated_vegattributes_dicts = json.load(f)

  # checks
  assert len(generated_vegattributes_dicts) == 2
  assert generated_vegattributes_dicts == [
    {
      "fdcId": 123456,
      "vegCategory": "UNCATEGORIZED",
    },
    {
      "fdcId": 654321,
      "vegCategory": "OMNI",
    },
  ]
