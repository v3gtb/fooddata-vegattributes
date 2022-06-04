from logging import getLogger
from typing import Set, TYPE_CHECKING

from .abstract_food_store import AbstractFoodStore
if TYPE_CHECKING:
  from .categorization import Categorizer
from . import description_based_heuristic
from .category import Category
from .food import Food


logger = getLogger(__name__)

def categorize(
  food: Food,
  categorizer: "Categorizer",
  food_store: AbstractFoodStore,
):
  logger.debug(
    "begin ingredient-based heuristic for %r (fdc ID: %s)",
    food.description,
    food.fdc_id,
  )

  input_food_categories: Set[Category] = set()
  for input_food_stub in food.input_food_stubs:
    logger.debug(
      "processing input food %r (ingredient code: %s)",
      input_food_stub.description,
      input_food_stub.ingredient_code,
    )
    assert input_food_stub.fdc_id != food.fdc_id

    try:
      input_food = food_store.get_by_ingredient_code(
        input_food_stub.ingredient_code
      )
      logger.debug("fooddata entry found for input food")
      input_food_category = categorizer.categorize(input_food).category
    except KeyError:
      logger.debug("no fooddata entry found for input food")
      input_food_category = description_based_heuristic.categorize(
        input_food_stub.description
      )

    logger.debug("input food categorized as %s", input_food_category.name)

    input_food_categories.add(input_food_category)

  # TODO this was taken from the description-based heuristic, only the names
  # changed => refactor
  if Category.OMNI in input_food_categories:
    return Category.OMNI
  if Category.VEGETARIAN_OR_OMNI in input_food_categories:
    return Category.VEGETARIAN_OR_OMNI
  if Category.VEGAN_VEGETARIAN_OR_OMNI in input_food_categories:
    if Category.VEGETARIAN in input_food_categories:
      return Category.VEGETARIAN_OR_OMNI
    return Category.VEGAN_VEGETARIAN_OR_OMNI
  if Category.VEGAN_OR_OMNI in input_food_categories:
    if Category.VEGETARIAN in input_food_categories:
      return Category.VEGETARIAN_OR_OMNI
    return Category.VEGAN_OR_OMNI
  if Category.VEGETARIAN in input_food_categories:
    return Category.VEGETARIAN
  if Category.VEGAN_OR_VEGETARIAN in input_food_categories:
    return Category.VEGAN_OR_VEGETARIAN
  if Category.VEGETARIAN in input_food_categories:
    return Category.VEGETARIAN
  if Category.VEGAN in input_food_categories:
    return Category.VEGAN
  return Category.UNCATEGORIZED
