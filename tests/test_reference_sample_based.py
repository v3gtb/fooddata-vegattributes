import csv
import json
from generate import Category, Food
from dataclasses import dataclass
import pytest
from typing import Dict, List

@dataclass
class ReferenceSample:
  food: Food
  expected_category: Category
  known_failure: bool = False

class IdNotInData(KeyError):
  pass

def load_food_ds_by_fdc_id_from_survey_fooddata_like_json(
  path, fdc_ids
) -> Dict[int, dict]:
  with open(path) as f:
    d = json.load(f)
  fdc_ids_to_food_ds = {}
  for food_d in d["SurveyFoods"]:
    fdc_id = food_d["fdcId"]
    if fdc_id in fdc_ids:
      fdc_ids_to_food_ds[fdc_id] = food_d
  not_found_ids = set(fdc_ids).difference(fdc_ids_to_food_ds.keys())
  if not_found_ids:
    raise IdNotInData("ids {', '.join(not_found_ids)} not present in data")
  return fdc_ids_to_food_ds

def load_foods_by_fdc_id_from_survey_fooddata_json(fdc_ids) -> Dict[int, Food]:
  cached_ref_json_path = (
    "ref_FoodData_Central_survey_food_json_2021-10-28.json"
  )
  try:
    print("trying to load from reference fooddata cache")
    fdc_ids_to_food_ds = load_food_ds_by_fdc_id_from_survey_fooddata_like_json(
      cached_ref_json_path, fdc_ids
    )
    print("successfully loaded from reference fooddata cache")
  except (FileNotFoundError, KeyError, json.JSONDecodeError):
    print("reference fooddata cache missing/incomplete, loading from source")
    fdc_ids_to_food_ds = load_food_ds_by_fdc_id_from_survey_fooddata_like_json(
      "FoodData_Central_survey_food_json_2021-10-28.json",
      fdc_ids,
    )
    print("writing reference fooddata cache")
    with open(cached_ref_json_path, "w") as f:
      json.dump({"SurveyFoods": list(fdc_ids_to_food_ds.values())}, f)
  return {
    fdc_id: Food.from_fdc_food_dict(food_d)
    for fdc_id, food_d in fdc_ids_to_food_ds.items()
  }

def load_reference_samples() -> List[ReferenceSample]:
  with open("reference_samples.csv") as f:
    reader = csv.DictReader(f)
    fdc_ids_to_sample_ds = {
      int(row["fdc_id"]): row for row in reader
    }
  fdc_ids = fdc_ids_to_sample_ds.keys()
  fdc_ids_to_foods = load_foods_by_fdc_id_from_survey_fooddata_json(fdc_ids)
  return [
    ReferenceSample(
      food=food,
      expected_category=(
        Category[fdc_ids_to_sample_ds[fdc_id]["expected_category"]]
      ),
      known_failure=(
        fdc_ids_to_sample_ds[fdc_id].get("known_failure", "N") == "Y"
      ),
    )
    for fdc_id, food in fdc_ids_to_foods.items()
  ]

def pytest_generate_tests(metafunc):
  reference_samples = load_reference_samples()
  if "reference_sample" in metafunc.fixturenames:
    metafunc.parametrize(
      "reference_sample",
      [
        pytest.param(
          reference_sample,
          marks=(
            [pytest.mark.xfail(strict=True)] if reference_sample.known_failure
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
  category = reference_sample.food.category
  expected_category = reference_sample.expected_category
  assert category == expected_category
