import json

from ..category import Category
from ..food import Food
from ..fooddata import load_survey_fooddata_dicts
from ..utils.random import select_n_random
from ..utils.terminal_ui import print_as_table

from .default_paths import default_dir_paths


def main():
  input_path = default_dir_paths.survey_fooddata_json
  food_ds = load_survey_fooddata_dicts(input_path)

  foods = [Food.from_fdc_food_dict(food_d) for food_d in food_ds]

  # go through all foods and assign categories
  foods_in_categories = {
    category: [] for category in Category
  }
  for food in foods:
    foods_in_categories[food.category].append(food)

  # stats
  print("numbers:")
  for category in Category:
    n_foods = len(foods_in_categories[category])
    print(f"{n_foods} {category.name}.")

  # export JSON
  for debug in ['debug_', '']:
    o = default_dir_paths.generated_vegattributes_json
    output_path = o.parent/(debug+o.name)
    with output_path.open("w") as f:
      json.dump(
        [
          food.as_fdc_like_dict(include_description=bool(debug))
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
