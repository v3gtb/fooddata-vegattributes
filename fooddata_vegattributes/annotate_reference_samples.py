import csv

from .reference_samples import load_reference_samples


def main():
  reference_samples = load_reference_samples()
  with open("reference_samples.csv", "w") as f:
    writer = csv.DictWriter(
      f,
      ["fdc_id", "expected_category", "known_failure", "description"],
      lineterminator="\n",
    )
    writer.writeheader()
    for reference_sample in reference_samples:
      writer.writerow({
        "fdc_id": reference_sample.food.fdc_id,
        "expected_category": reference_sample.expected_category.name,
        "known_failure": "Y" if reference_sample.known_failure else "N",
        "description": reference_sample.food.description,
      })


if __name__ == "__main__":
  main()
