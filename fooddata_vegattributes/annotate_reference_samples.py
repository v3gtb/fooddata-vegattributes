from .csv_reference_sample_store import CsvReferenceSampleStore
from .indexed_fooddata_food_store import IndexedFoodDataFoodStore


def main():
  with IndexedFoodDataFoodStore.from_path(
    "indexed_FoodData_Central_survey_food_json_2021-10-28.jsons.tar.xz"
  ) as food_store, (
    CsvReferenceSampleStore.from_path_and_food_store(
      "reference_samples.csv",
      food_store
    )
  ) as reference_sample_store:
    reference_samples = reference_sample_store.get_all()
    reference_sample_store.reference_samples_csv\
    .reset_and_write_reference_sample_dicts(
      {
        "fdc_id": reference_sample.food.fdc_id,
        "expected_category": reference_sample.expected_category.name,
        "known_failure": reference_sample.known_failure,
        "description": reference_sample.food.description,
      }
      for reference_sample in reference_samples
    )


if __name__ == "__main__":
  main()
