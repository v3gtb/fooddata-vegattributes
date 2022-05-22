import random

from ..csv_reference_sample_store import CsvReferenceSampleStore
from ..food import Category
from ..fdc_app import get_fdc_app_details_url
from ..indexed_fooddata_food_store import IndexedFoodDataFoodStore
from ..reference_sample import ReferenceSample

from .default_paths import default_dir_paths

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
    fdc_ids_with_ref = set(reference_sample_store.iter_all_fdc_ids())
    fdc_ids_without_ref = [
      fdc_id for fdc_id in
      food_store.get_all_fdc_ids()
      if fdc_id not in fdc_ids_with_ref
    ]
    while True:
      fdc_id = random.choice(fdc_ids_without_ref)
      foods = food_store.get_mapped_by_fdc_ids([fdc_id])
      food = foods[fdc_id]
      print(f"FDC ID: {food.fdc_id}")
      print(f"Description: {food.description}")
      print(f"URL: {get_fdc_app_details_url(food.fdc_id)}")
      print("Category shortcuts:")
      for shortcut, category in shortcut_to_category.items():
        print(f"- {shortcut}: {category.name}")
      try:
        inp = input("Input category or s to skip, q/Ctrl-D to quit: ")
      except EOFError:
        print()
        return
      if inp.lower() == "q":
        return
      elif inp.lower() == "s":
        print()
        continue
      category = shortcut_to_category[inp]
      print(category.name)
      reference_sample = ReferenceSample(
        food=food,
        expected_category=category,
        description=food.description
      )
      print("Appending...", end="")
      reference_sample_store.append(reference_sample)
      fdc_ids_with_ref.add(fdc_id)
      fdc_ids_without_ref.remove(fdc_id)
      print("\n")


if __name__ == "__main__":
  main()
