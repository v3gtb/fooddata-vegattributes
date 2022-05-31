from logging import getLogger
from typing import TYPE_CHECKING

from .abstract_food_store import AbstractFoodStore
if TYPE_CHECKING:
  from .categorization import Categorizer
from . import description_based_heuristic
from . import ingredient_based_heuristic
from .category import Category
from .food import Food


logger = getLogger(__name__)

def categorize(
  food: Food,
  categorizer: "Categorizer",
  food_store: AbstractFoodStore,
):
  ingredient_based_category = ingredient_based_heuristic.categorize(
    food,
    categorizer=categorizer,
    food_store=food_store,
  )
  if ingredient_based_category == Category.UNCATEGORIZED:
    return description_based_heuristic.categorize(food.description)
  return ingredient_based_category
