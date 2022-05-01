from contextlib import ExitStack
import csv
from io import BytesIO
import json
from dataclasses import dataclass
from datetime import datetime
from os import PathLike
from pathlib import Path
import pytest
from tarfile import (
  open as tarfile_open, ReadError as TarFileReadError, TarFile, TarInfo
)
from typing import Dict, List, Union

from fooddata_vegattributes.generate import Category, Food

@dataclass
class ReferenceSample:
  food: Food
  expected_category: Category
  known_failure: bool = False

class IdNotInData(KeyError):
  pass

class CompressedIndexedFoodDataJson:
  """
  Compressed, indexed (by FDC ID) FoodData JSON entries stored in a file.
  """
  def __init__(self, tarfile: TarFile):
    self.tarfile = tarfile
    self.close_stack = ExitStack()

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "CompressedIndexedFoodDataJson":
    """
    Opens archive for reading or writing depending on the given mode.

    If mode is `"w"`, we default to using LZMA compression. Use `"w:[method]"`
    for other compression methods and leave `[method]` empty to force no
    compression.
    """
    if mode == "w":
      mode = "w:xz"
    tarfile = tarfile_open(path, mode=mode)
    obj = cls(tarfile=tarfile)
    obj.close_stack.enter_context(tarfile)
    return obj

  def close(self):
    self.close_stack.close()

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    self.close()

  def write_fooddata_dicts(self, ds: List[Dict]):
    for d in ds:
      fdc_id_str = str(d["fdcId"])
      json_bytes = json.dumps(d).encode("utf-8")
      tar_info = TarInfo(name=fdc_id_str)
      tar_info.size = len(json_bytes)
      tar_info.mtime = datetime.now().timestamp()
      self.tarfile.addfile(tar_info, BytesIO(json_bytes))

  def get_fooddata_dict_by_fdc_id(self, fdc_id: Union[int, str]):
    fdc_id_str = str(fdc_id)
    return json.load(self.tarfile.extractfile(fdc_id_str))


def load_foods_by_fdc_id_from_compressed_indexed_fooddata_json(
  fdc_ids
) -> Dict[int, Food]:
  """
  Name is a bit of a misnomer, as it also regenerates the indexed JSON.
  """
  compressed_indexed_json_path = Path(
    "indexed_FoodData_Central_survey_food_json_2021-10-28.jsons.tar.xz"
  )
  for attempt in range(2):
    try:
      print("trying to load from indexed JSON")
      with CompressedIndexedFoodDataJson.from_path(
        compressed_indexed_json_path
      ) as cifj:
        fdc_ids_to_food_ds = {
          fdc_id: cifj.get_fooddata_dict_by_fdc_id(fdc_id)
          for fdc_id in fdc_ids
        }
      print("successfully loaded from indexed JSON")
      break
    except (FileNotFoundError, KeyError, TarFileReadError):
      if attempt > 0:
        raise
      print("indexed JSON missing or malformed, (re)generating")
      with open("FoodData_Central_survey_food_json_2021-10-28.json") as f:
        food_ds = json.load(f)["SurveyFoods"]
      with CompressedIndexedFoodDataJson.from_path(
        compressed_indexed_json_path, "w"
      ) as cifj:
        cifj.write_fooddata_dicts(food_ds)
      print("done writing indexed JSON, trying to load again")
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
  fdc_ids_to_foods = (
    load_foods_by_fdc_id_from_compressed_indexed_fooddata_json(fdc_ids)
  )
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
