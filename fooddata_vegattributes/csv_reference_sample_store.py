from contextlib import ExitStack
from dataclasses import dataclass, field
from typing import Iterable, Sequence, Mapping, Optional

from .abstract_reference_sample_store import AbstractReferenceSampleStore
from .abstract_food_store import AbstractFoodStore
from .category import Category
from .reference_sample import ReferenceSample
from .reference_samples_csv import ReferenceSamplesCsv, ReferenceSampleDict
from .utils.close_on_exit import CloseOnExit


@dataclass
class CsvReferenceSampleStore(AbstractReferenceSampleStore, CloseOnExit):
  reference_samples_csv: ReferenceSamplesCsv
  food_store: AbstractFoodStore
  close_stack: ExitStack = field(init=False, default_factory=ExitStack)

  @classmethod
  def from_path_and_food_store(cls, path, food_store, create=False):
    mode = "a+" if create else "r+"
    reference_samples_csv = ReferenceSamplesCsv.from_path(path, mode)
    if create:
      reference_samples_csv.write_header_if_empty()
    obj = cls(
      reference_samples_csv=reference_samples_csv,
      food_store=food_store,
    )
    obj.close_stack.enter_context(reference_samples_csv)
    return obj

  def close(self):
    self.close_stack.close()

  def iter_all(self) -> Iterable[ReferenceSample]:
    return (
      ReferenceSample(
        fdc_id=d["fdc_id"],
        expected_category=(
          Category[d["expected_category"]]
        ),
        known_failure=d["known_failure"],
      )
      for d in self._read_all_reference_sample_dicts()
    )

  def get_all_mapped_by_fdc_ids(self) -> Mapping[int, ReferenceSample]:
    return {
      reference_sample.fdc_id: reference_sample
      for reference_sample in self.iter_all()
    }

  def iter_all_fdc_ids(self) -> Iterable[int]:
    return (
      d["fdc_id"] for d in self._read_all_reference_sample_dicts()
    )

  def reset_and_put_all(self, reference_samples: Sequence[ReferenceSample]):
    fdc_ids = set(sample.fdc_id for sample in reference_samples)
    foods_by_fdc_id = self.food_store.get_mapped_by_fdc_ids(fdc_ids)
    self.reference_samples_csv.reset_and_write_reference_sample_dicts(
      _reference_sample_to_dict(
        reference_sample,
        description=(
          foods_by_fdc_id[reference_sample.fdc_id].description
          if reference_sample.fdc_id in foods_by_fdc_id
          else None
        ),
      )
      for reference_sample in reference_samples
    )

  def append(self, reference_sample: ReferenceSample):
    self.reference_samples_csv.append_reference_sample_dict(
      _reference_sample_to_dict(
        reference_sample,
        description=(
          self.food_store.get_by_fdc_id(reference_sample.fdc_id).description
        ),
      )
    )

  def _read_all_reference_sample_dicts(self) -> Iterable[ReferenceSampleDict]:
    "Convenience/shortcut method"
    return self.reference_samples_csv.read_all_reference_sample_dicts()

def _reference_sample_to_dict(
  reference_sample: ReferenceSample, description: Optional[str]
) -> ReferenceSampleDict:
  return {
    "fdc_id": reference_sample.fdc_id,
    "expected_category": reference_sample.expected_category.name,
    "known_failure": reference_sample.known_failure,
    "description": description,
  }
