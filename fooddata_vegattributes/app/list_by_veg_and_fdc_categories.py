from ..categorization import Categorizer
from ..category import Category

from .with_default_paths import default_food_and_reference_sample_stores


def main(fdc_category_description: str, veg_category: Category):
  with default_food_and_reference_sample_stores() as (
    food_store, reference_sample_store
  ):
    foods_in_fdc_category = food_store.get_mapped_by_fdc_category(
      fdc_category_description
    ).values()
    categorizer = Categorizer(
      reference_sample_store=reference_sample_store,
      food_store=food_store,
    )
    for food in foods_in_fdc_category:
      if categorizer.categorize(food).category == veg_category:
        print(food)
