from collections import ChainMap
from dataclasses import dataclass
import json
from pathlib import Path
import pytest
from typing import List

from fooddata_vegattributes.fooddata import FoodDataDict
from fooddata_vegattributes.reference_samples_csv import (
  ReferenceSamplesCsv,
  ReferenceSampleDict,
)


# food data

@dataclass
class FakeFoodDataJson:
  food_data_dicts: List[FoodDataDict]
  path: Path

@dataclass
class FakeFoodDataJsons:
  survey: FakeFoodDataJson
  sr_legacy: FakeFoodDataJson

@pytest.fixture
def fake_food_data():
  return [
    {
      "fdcId": 123456,
      "description": "A fake food, salted",
      "inputFoods": [],
      "foodCode": 9876543,
    }
  ]

@pytest.fixture
def fake_survey_fooddata_json(
  tmp_path: Path, fake_food_data: List[FoodDataDict]
):
  json_path = tmp_path/"fake_survey_fooddata.json"

  with json_path.open("w") as f:
    json.dump({ "SurveyFoods": fake_food_data }, f)

  yield FakeFoodDataJson(food_data_dicts=fake_food_data, path=json_path)

@pytest.fixture
def fake_sr_legacy_fooddata_json(tmp_path: Path):
  json_path = tmp_path/"fake_sr_legacy_fooddata.json"

  # TODO make non-empty once randomness in input test has been taken care of
  fake_food_data = []

  with json_path.open("w") as f:
    json.dump({ "SRLegacyFoods": fake_food_data }, f)

  yield FakeFoodDataJson(food_data_dicts=fake_food_data, path=json_path)

@pytest.fixture
def fake_fooddata_jsons(
  fake_survey_fooddata_json: FakeFoodDataJson,
  fake_sr_legacy_fooddata_json: FakeFoodDataJson,
):
  return FakeFoodDataJsons(
    survey=fake_survey_fooddata_json, sr_legacy=fake_sr_legacy_fooddata_json
  )

# reference samples

@pytest.fixture
def fake_reference_sample_dicts(fake_food_data: List[FoodDataDict]):
  return [
    dict(
      fdc_id=food_data_dict["fdcId"],
      expected_category="VEGAN",
      known_failure=False,
      description=None
    )
    for food_data_dict in fake_food_data
  ]

@dataclass
class FakeReferenceSampleCsv:
  reference_sample_dicts: List[ReferenceSampleDict]
  path: Path

@pytest.fixture
def create_fake_reference_samples_csv(tmp_path):
  def _create_fake_reference_samples_csv(
    reference_sample_dicts: List[ReferenceSampleDict]
  ) -> FakeReferenceSampleCsv:
    csv_path = tmp_path/"reference_samples.csv"
    with ReferenceSamplesCsv.from_path(csv_path, "w") as ref_csv:
      ref_csv.reset_and_write_reference_sample_dicts(reference_sample_dicts)
    return FakeReferenceSampleCsv(
      reference_sample_dicts=reference_sample_dicts,
      path=csv_path,
    )
  return _create_fake_reference_samples_csv

@pytest.fixture
def fake_reference_samples_csv(
  fake_reference_sample_dicts,
  create_fake_reference_samples_csv,
):
  yield create_fake_reference_samples_csv(fake_reference_sample_dicts)

@pytest.fixture
def fake_reference_samples_csv_no_description(
  fake_reference_sample_dicts,
  create_fake_reference_samples_csv,
):
  fake_reference_sample_dicts = [
    ChainMap({"description": None}, d) for d in fake_reference_sample_dicts
  ]
  yield create_fake_reference_samples_csv(fake_reference_sample_dicts)
