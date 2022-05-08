from dataclasses import dataclass
from typing import Optional

from .food import Category, Food

@dataclass
class ReferenceSample:
  food: Food
  expected_category: Category
  known_failure: bool = False
  description: Optional[str] = None
