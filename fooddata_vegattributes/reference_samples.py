import csv
from dataclasses import dataclass
from typing import Dict, List, Optional

from .food import Category, Food
from .indexed_fooddata import ensure_compressed_indexed_fooddata_json

@dataclass
class ReferenceSample:
  food: Food
  expected_category: Category
  known_failure: bool = False
  description: Optional[str] = None

def load_reference_samples() -> List[ReferenceSample]:
  with open("reference_samples.csv") as f:
    reader = csv.DictReader(f)
    fdc_ids_to_sample_ds = {
      int(row["fdc_id"]): row for row in reader
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
      known_failure=(
        fdc_ids_to_sample_ds[fdc_id].get("known_failure", "N") == "Y"
      ),
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
