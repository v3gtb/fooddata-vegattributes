from collections import defaultdict
import json
from os import environ
from pathlib import Path

from generate import Category

json_path = (
  "debug_VegAttributes_for_FoodData_Central_survey_food_json_2021-10-28.json"
)

def main():
  with open(json_path) as f:
    food_ds = json.load(f)

  food_ds_by_category = defaultdict(lambda: [])
  for food_d in food_ds:
    food_ds_by_category[food_d["vegCategory"]].append(food_d)

  output_dir = Path(environ.get("OUTPUT_DIR") or ".gh-pages/content")
  output_dir.mkdir(exist_ok=True)
  lists_output_dir = output_dir/"category-lists"
  lists_output_dir.mkdir(exist_ok=True)
  with (output_dir/"categories-toc.md").open("w") as toc_f:
    for category in Category:
      name = category.name
      foods = food_ds_by_category[name]
      md_name = name.lower().replace("_", "-")
      toc_f.write(
        f"- [{name}](category-lists/{md_name}) ({len(foods)} entries)\n"
      )
      list_md_path = (lists_output_dir/md_name).with_suffix(".md")
      with list_md_path.open("w") as list_f:
        for food in sorted(foods, key=lambda x: x["description"]):
          list_f.write(f"- {food['description']} (fdcId: {food['fdcId']})\n")


if __name__ == "__main__":
  main()
