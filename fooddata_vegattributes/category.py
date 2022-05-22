from enum import auto

from .utils.enum import AutoStrEnum


class Category(AutoStrEnum):
  VEGAN = auto()
  VEGAN_OR_VEGETARIAN = auto()
  VEGETARIAN = auto()
  VEGAN_OR_OMNI = auto()
  VEGAN_VEGETARIAN_OR_OMNI = auto()
  VEGETARIAN_OR_OMNI = auto()
  OMNI = auto()
  UNCATEGORIZED = auto()
