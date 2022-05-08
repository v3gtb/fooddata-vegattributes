from typing import Dict, List

from .food import Category, Food
from .indexed_fooddata import ensure_compressed_indexed_fooddata_json
from .reference_sample import ReferenceSample
from .reference_samples_csv import ReferenceSamplesCsv


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
