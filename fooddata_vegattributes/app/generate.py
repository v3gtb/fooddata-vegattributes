import json
from typing import Dict

from ..category import Category
from ..categorization import Categorization, Categorizer
from ..food import Food
from ..fooddata import (
  load_survey_fooddata_dicts,
  load_sr_legacy_fooddata_dicts,
)
from ..utils.random import select_n_random
from ..utils.terminal_ui import print_as_table
from ..vegattributes_dict import (
  vegattributes_dict_from_food,
  verbose_vegattributes_dict_from_food,
)

from .default_paths import default_dir_paths
from .with_default_paths import default_food_and_reference_sample_stores


def main():
  food_ds = (
    load_survey_fooddata_dicts(default_dir_paths.survey_fooddata_json) +
    load_sr_legacy_fooddata_dicts(default_dir_paths.sr_legacy_fooddata_json)
  )

  foods = [Food.from_fdc_food_dict(food_d) for food_d in food_ds]

  # go through all foods and assign categories
  foods_in_categories = {
    category: [] for category in Category
  }
  food_categorizations: Dict[Food, Categorization] = {}
  with default_food_and_reference_sample_stores() as (
    food_store, reference_sample_store
  ):
    categorizer = Categorizer(reference_sample_store=reference_sample_store)
    for food in foods:
      categorization = categorizer.categorize(food)
      foods_in_categories[categorization.category].append(food)
      food_categorizations[food] = categorization

  # stats
  print("numbers:")
  for category in Category:
    n_foods = len(foods_in_categories[category])
    print(f"{n_foods} {category.name}.")

  # export JSON
  for debug in ['debug_', '']:
    dict_from_food_func = (
      vegattributes_dict_from_food if not debug
      else verbose_vegattributes_dict_from_food
    )
    o = default_dir_paths.generated_vegattributes_json
    output_path = o.parent/(debug+o.name)
    with output_path.open("w") as f:
      json.dump(
        [
          dict_from_food_func(
            food,
            categorization=food_categorizations[food],
          )
          for food in foods
        ],
        f
      )

  # output sample
  print("sample:")
  n_samples = 10
  category_samples = {
    category: select_n_random(
      foods_in_categories[category],
      n_samples,
      pad=lambda: Food(fdc_id=-1, description="")
    )
    for category in Category
  }

  print_as_table(
    [[category.name.replace("_", " ") for category in Category]]
    +
    [
      # alternate food item description rows and empty rows
      x for y in
      zip(
        # food item description row
        [
          [desc.description for desc in descs]
          for descs
          in zip(*(category_samples[category] for category in Category))
        ],
      )
      for x in y
    ]
  )
