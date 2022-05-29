from dataclasses import dataclass
from typing import Dict, Optional

from . import description_based_heuristic
from .abstract_reference_sample_store import AbstractReferenceSampleStore
from .category import Category
from .food import Food
from .reference_sample import ReferenceSample


@dataclass
class Categorizer:
  reference_sample_store: AbstractReferenceSampleStore
  _cached_reference_samples_by_fdc_id: Optional[Dict[int, ReferenceSample]] = (
    None
  )
  """
  Note: Only loads reference samples once for now, but this should be changed
  eventually using a caching wrapper around the reference sample store (which
  would then also have a get_by_fdc_id method - no point right now because it'd
  be horribly inefficient).
  """
  def categorize(self, food: Food) -> Category:
    return (
      getattr(
        self._reference_samples_by_fdc_id.get(food.fdc_id),
        "expected_category",
        None
      )
      or description_based_heuristic.categorize(food.description)
    )

  @property
  def _reference_samples_by_fdc_id(self):
    if not self._cached_reference_samples_by_fdc_id:
      self._cached_reference_samples_by_fdc_id = (
        self.reference_sample_store.get_all_mapped_by_fdc_ids()
      )
    return self._cached_reference_samples_by_fdc_id
