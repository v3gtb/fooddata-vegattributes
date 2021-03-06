from dataclasses import dataclass, field
from enum import auto
from typing import Dict, Mapping, Optional

from . import combined_heuristic
from .abstract_food_store import AbstractFoodStore
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
  discrepancies: Mapping[CategorizationSource, Category] = field(
    default_factory=dict
  )

@dataclass
class Categorizer:
  """
  Note: Only loads reference samples once for now, but this should be changed
  eventually using a caching wrapper around the reference sample store (which
  would then also have a get_by_fdc_id method - no point right now because it'd
  be horribly inefficient).
  """
  reference_sample_store: AbstractReferenceSampleStore
  food_store: AbstractFoodStore
  _cached_reference_samples_by_fdc_id: Optional[Dict[int, ReferenceSample]] = (
    None
  )

  def categorize(self, food: Food) -> Categorization:
    ref = self._reference_samples_by_fdc_id.get(food.fdc_id)
    heuristic_based_category = combined_heuristic.categorize(
      food, self, self.food_store
    )
    discrepancies = {}
    if ref is not None:
      category = ref.expected_category
      source = CategorizationSource.REFERENCE
      if category != heuristic_based_category:
        discrepancies = {
          CategorizationSource.HEURISTIC: heuristic_based_category
        }
    else:
      category = heuristic_based_category
      source = CategorizationSource.HEURISTIC
    return Categorization(
      category=category, source=source, discrepancies=discrepancies
    )

  @property
  def _reference_samples_by_fdc_id(self):
    if not self._cached_reference_samples_by_fdc_id:
      self._cached_reference_samples_by_fdc_id = (
        self.reference_sample_store.get_all_mapped_by_fdc_ids()
      )
    return self._cached_reference_samples_by_fdc_id
