from contextlib import ExitStack
from dataclasses import dataclass, field
from typing import List

from .abstract_food_store import AbstractFoodStore
from .abstract_reference_sample_store import AbstractReferenceSampleStore
from .food import Category
from .reference_sample import ReferenceSample
from .reference_samples_csv import ReferenceSamplesCsv


@dataclass
class CsvReferenceSampleStore(AbstractReferenceSampleStore):
  reference_samples_csv: ReferenceSamplesCsv
  food_store: AbstractFoodStore
  close_stack: ExitStack = field(init=False, default_factory=ExitStack)

  @classmethod
  def from_path_and_food_store(cls, path, food_store):
    reference_samples_csv = ReferenceSamplesCsv.from_path(path)
    obj = cls(
      reference_samples_csv=reference_samples_csv,
      food_store=food_store
    )
    obj.close_stack.enter_context(reference_samples_csv)
    return obj

  def close(self):
    self.close_stack.close()

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    self.close()

  def get_all(self) -> List[ReferenceSample]:
    reference_sample_ds = (
      self.reference_samples_csv.read_all_reference_sample_dicts()
    )
    fdc_ids_to_ds = {
      d["fdc_id"]: d for d in reference_sample_ds
    }
    fdc_ids_to_foods = (
      self.food_store.get_mapped_by_fdc_ids(fdc_ids_to_ds.keys())
    )
    return [
      ReferenceSample(
        food=food,
        expected_category=(
          Category[fdc_ids_to_ds[fdc_id]["expected_category"]]
        ),
        known_failure=fdc_ids_to_ds[fdc_id]["known_failure"],
      )
      for fdc_id, food in fdc_ids_to_foods.items()
    ]

  def reset_and_put_all(self, reference_samples: List[ReferenceSample]):
    self.reference_samples_csv.reset_and_write_reference_sample_dicts(
      {
        "fdc_id": reference_sample.food.fdc_id,
        "expected_category": reference_sample.expected_category.name,
        "known_failure": reference_sample.known_failure,
        "description": reference_sample.food.description,
      }
      for reference_sample in reference_samples
    )
