from collections import defaultdict
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
  print("loading foods from JSON... ", end="")
  food_ds = (
    load_survey_fooddata_dicts(default_dir_paths.survey_fooddata_json) +
    load_sr_legacy_fooddata_dicts(default_dir_paths.sr_legacy_fooddata_json)
  )
  print("done")

  foods = [Food.from_fdc_food_dict(food_d) for food_d in food_ds]

  # go through all foods and assign categories
  print("categorizing foods... ", end="")
  foods_in_categories = {
    category: [] for category in Category
  }
  fdc_categories_to_foods_in_veg_categories = defaultdict(
    lambda: { veg_category: [] for veg_category in Category }
  )
  food_categorizations: Dict[Food, Categorization] = {}
  with default_food_and_reference_sample_stores() as (
    food_store, reference_sample_store
  ):
    categorizer = Categorizer(
      reference_sample_store=reference_sample_store,
      food_store=food_store,
    )
    print("    ", end="")
    for i, food in enumerate(foods):
      print(f"\b\b\b\b{i/len(foods)*100:>3.0f}%", end="")
      categorization = categorizer.categorize(food)
      food_categorizations[food] = categorization
      foods_in_categories[categorization.category].append(food)
      fdc_categories_to_foods_in_veg_categories[
        food.fdc_category_description
      ][categorization.category].append(food)
    print("done")

  # stats
  print("numbers:")
  for category in Category:
    n_foods = len(foods_in_categories[category])
    print(f"{n_foods} {category.name}.")
  print("\n")

  # stats per FDC category
  print("numbers by FDC category:\n")
  for fdc_category, veg_categories_items in sorted(
    fdc_categories_to_foods_in_veg_categories.items(),
    key=lambda x: x[0]
  ):
    print(f"  {fdc_category}")
    for veg_category, items in veg_categories_items.items():
      n_foods = len(items)
      if not n_foods:
        continue
      print(f"    {n_foods} {veg_category.name}.")
    print("")
  print("")

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
      pad=lambda: Food(
        fdc_id=-1, food_code=-1, description="", input_food_stubs=(),
        fdc_category_description="",
      )
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
