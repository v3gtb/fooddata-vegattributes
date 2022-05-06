from contextlib import ExitStack
import csv
from dataclasses import dataclass
from os import PathLike
from typing import Dict, Generator, List, Optional, TypedDict, Union

from .food import Category, Food
from .indexed_fooddata import ensure_compressed_indexed_fooddata_json

@dataclass
class ReferenceSample:
  food: Food
  expected_category: Category
  known_failure: bool = False
  description: Optional[str] = None

class ReferenceSampleDict(TypedDict):
  fdc_id: int
  expected_category: str
  known_failure: bool
  description: Optional[str]

class ReferenceSamplesCsv:
  """
  CSV file containing reference samples.
  """
  def __init__(self, file, csv_io: Union[csv.DictWriter, csv.DictReader]):
    self.file = file
    self.close_stack = ExitStack()
    self.csv_io = csv_io

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "ReferenceSamplesCsv":
    """
    Opens CSV file for reading or writing depending on the given mode.
    """
    file = open(path, mode)
    csv_io: Union[csv.DictWriter, csv.DictReader]
    if mode == "w" or mode == "a":
      csv_io = csv.DictWriter(
        file,
        ["fdc_id", "expected_category", "known_failure", "description"],
        lineterminator="\n",
      )
      if mode != "a":
        csv_io.writeheader()
    elif mode == "r":
      csv_io = csv.DictReader(file)
    else:
      raise ValueError("mode must be one of 'r', or 'w' or 'a'")
    obj = cls(file=file, csv_io=csv_io)
    obj.close_stack.enter_context(file)
    return obj

  def close(self):
    self.close_stack.close()

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    self.close()

  def write_reference_sample_dict(self, d: ReferenceSampleDict):
    assert isinstance(self.csv_io, csv.DictWriter)
    self.csv_io.writerow({
      "fdc_id": d["fdc_id"],
      "expected_category": d["expected_category"],
      "known_failure": "Y" if d["known_failure"] else "N",
      "description": d.get("description"),
    })

  def get_reference_sample_dicts(self) \
  -> Generator[ReferenceSampleDict, None, None]:
    assert isinstance(self.csv_io, csv.DictReader)
    for row in self.csv_io:
      yield {
        "fdc_id": int(row["fdc_id"]),
        "expected_category": row["expected_category"],
        "known_failure": row["known_failure"] == "Y",
        "description": row.get("description"),
      }


def load_reference_samples() -> List[ReferenceSample]:
  with ReferenceSamplesCsv.from_path("reference_samples.csv", "r") \
  as reference_samples_csv:
    fdc_ids_to_sample_ds = {
      sample_d["fdc_id"]: sample_d
      for sample_d in reference_samples_csv.get_reference_sample_dicts()
    }
  fdc_ids = fdc_ids_to_sample_ds.keys()
  fdc_ids_to_foods = (
    _load_foods_by_fdc_id_from_compressed_indexed_fooddata_json(fdc_ids)
  )
  return [
    ReferenceSample(
      food=food,
      expected_category=(
        Category[fdc_ids_to_sample_ds[fdc_id]["expected_category"]]
      ),
      known_failure=fdc_ids_to_sample_ds[fdc_id]["known_failure"],
    )
    for fdc_id, food in fdc_ids_to_foods.items()
  ]

# TODO make public, clean up, rename and move to a more appropriate place
def _load_foods_by_fdc_id_from_compressed_indexed_fooddata_json(
  fdc_ids
) -> Dict[int, Food]:
  """
  Name is a bit of a misnomer, as it also regenerates the indexed JSON.
  """
  with ensure_compressed_indexed_fooddata_json() as cifj:
    fdc_ids_to_food_ds = {
      fdc_id: cifj.get_fooddata_dict_by_fdc_id(fdc_id)
      for fdc_id in fdc_ids
    }
  return {
   fdc_id: Food.from_fdc_food_dict(food_d)
   for fdc_id, food_d in fdc_ids_to_food_ds.items()
  }
