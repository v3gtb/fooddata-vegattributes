from collections import defaultdict
import json
from os import environ
from pathlib import Path

from fooddata_vegattributes.app.default_paths import default_dir_paths
from fooddata_vegattributes.category import Category
from fooddata_vegattributes.fdc_app import get_fdc_app_details_url
from fooddata_vegattributes.reference_samples_csv import ReferenceSamplesCsv

json_path = (
  f"debug_{default_dir_paths.generated_vegattributes_json}"
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
          fdc_id = food["fdcId"]
          description = food["description"]
          source = food["vegCategorySource"].lower()
          comma_sep_discrepancies = ", ".join(
            f"{disc_source.lower()}: {disc_category.lower()}"
            for disc_source, disc_category in
            food.get("vegCategoryDiscrepancies", {}).items()
          )
          optional_discrepancies = (
            f'; <span style="color: red;">{comma_sep_discrepancies}</span>'
            if comma_sep_discrepancies else ''
          )
          url = get_fdc_app_details_url(fdc_id)
          list_f.write(
            f"- {description} (fdcId: [{fdc_id}]({url}); "
            f"via {source}{optional_discrepancies})\n"
          )

  data_dir = output_dir/"_data"
  data_dir.mkdir(exist_ok=True)
  with ReferenceSamplesCsv.from_path(
    default_dir_paths.reference_samples_csv
  ) as reference_samples_csv, (
    data_dir/"stats.yml"
  ).open("w") as stats_file:
    reference_sample_dicts = list(
      reference_samples_csv.read_all_reference_sample_dicts()
    )
    n_known_failures = sum(
      1 for r in reference_sample_dicts if r["known_failure"]
    )
    failure_fraction = n_known_failures / len(reference_sample_dicts)
    stats_file.write(f"failure_percentage: {failure_fraction*100:.1f}\n")



if __name__ == "__main__":
  main()
