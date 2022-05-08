from .reference_samples_io import load_reference_samples
from .reference_samples_csv import ReferenceSamplesCsv


def main():
  reference_samples = load_reference_samples()
  with ReferenceSamplesCsv.from_path("reference_samples.csv", "w") \
  as reference_samples_csv:
    for reference_sample in reference_samples:
      reference_samples_csv.write_reference_sample_dict({
        "fdc_id": reference_sample.food.fdc_id,
        "expected_category": reference_sample.expected_category.name,
        "known_failure": reference_sample.known_failure,
        "description": reference_sample.food.description,
      })


if __name__ == "__main__":
  main()
