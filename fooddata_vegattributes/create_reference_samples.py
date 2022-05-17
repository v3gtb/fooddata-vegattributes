import random

from .csv_reference_sample_store import CsvReferenceSampleStore
from .default_paths import default_dir_paths
from .food import Category
from .fdc_app import get_fdc_app_details_url
from .indexed_fooddata_food_store import IndexedFoodDataFoodStore
from .reference_sample import ReferenceSample


shortcut_to_category = {
  "veg": Category.VEGAN,
  "vov": Category.VEGAN_OR_VEGETARIAN,
  "vgt": Category.VEGETARIAN,
  "vgo": Category.VEGAN_OR_OMNI,
  "vvo": Category.VEGAN_VEGETARIAN_OR_OMNI,
  "vto": Category.VEGETARIAN_OR_OMNI,
  "o": Category.OMNI,
}

def main():
  with IndexedFoodDataFoodStore.from_path(
    default_dir_paths.compressed_indexed_fooddata_json
  ) as food_store, (
    CsvReferenceSampleStore.from_path_and_food_store(
      default_dir_paths.reference_samples_csv,
      food_store,
    )
  ) as reference_sample_store:
    all_fdc_ids = food_store.get_all_fdc_ids()
    while True:
      fdc_id = random.choice(all_fdc_ids)
      foods = food_store.get_mapped_by_fdc_ids([fdc_id])
      food = foods[fdc_id]
      print(f"FDC ID: {food.fdc_id}")
      print(f"Description: {food.description}")
      print(f"URL: {get_fdc_app_details_url(food.fdc_id)}")
      print("Category shortcuts:")
      for shortcut, category in shortcut_to_category.items():
        print(f"- {shortcut}: {category.name}")
      try:
        inp = input("Input category or q/Ctrl-D to quit: ")
      except EOFError:
        print()
        return
      if inp.lower() == "q":
        return
      category = shortcut_to_category[inp]
      print(category.name)
      reference_sample = ReferenceSample(
        food=food,
        expected_category=category,
        description=food.description
      )
      print("Appending...", end="")
      reference_sample_store.append(reference_sample)
      print("\n")


if __name__ == "__main__":
  main()
