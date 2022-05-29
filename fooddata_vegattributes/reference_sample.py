from dataclasses import dataclass

from .category import Category


@dataclass
class ReferenceSample:
  fdc_id: int
  expected_category: Category
  known_failure: bool = False
