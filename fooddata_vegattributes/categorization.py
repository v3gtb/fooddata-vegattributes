from . import description_based_heuristic
from .category import Category
from .food import Food


def categorize(food: Food) -> Category:
  return description_based_heuristic.categorize(food.description)
