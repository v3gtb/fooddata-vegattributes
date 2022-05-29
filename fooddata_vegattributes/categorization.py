from dataclasses import dataclass
from enum import auto
from typing import Dict, Optional

from . import description_based_heuristic
from .abstract_reference_sample_store import AbstractReferenceSampleStore
from .category import Category
from .food import Food
from .reference_sample import ReferenceSample
from .utils.enum import AutoStrEnum


class CategorizationSource(AutoStrEnum):
  HEURISTIC = auto()
  REFERENCE = auto()

@dataclass
class Categorization:
  category: Category
  source: CategorizationSource

@dataclass
class Categorizer:
  """
  Note: Only loads reference samples once for now, but this should be changed
  eventually using a caching wrapper around the reference sample store (which
  would then also have a get_by_fdc_id method - no point right now because it'd
  be horribly inefficient).
  """
  reference_sample_store: AbstractReferenceSampleStore
  _cached_reference_samples_by_fdc_id: Optional[Dict[int, ReferenceSample]] = (
    None
  )

  def categorize(self, food: Food) -> Categorization:
    ref = self._reference_samples_by_fdc_id.get(food.fdc_id)
    if ref is not None:
      category = ref.expected_category
      source = CategorizationSource.REFERENCE
    else:
      category = description_based_heuristic.categorize(food.description)
      source = CategorizationSource.HEURISTIC
    return Categorization(category=category, source=source)

  @property
  def _reference_samples_by_fdc_id(self):
    if not self._cached_reference_samples_by_fdc_id:
      self._cached_reference_samples_by_fdc_id = (
        self.reference_sample_store.get_all_mapped_by_fdc_ids()
      )
    return self._cached_reference_samples_by_fdc_id
