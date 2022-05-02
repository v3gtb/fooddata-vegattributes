import pytest

from fooddata_vegattributes.reference_samples import load_reference_samples

def pytest_generate_tests(metafunc):
  reference_samples = load_reference_samples()
  if "reference_sample" in metafunc.fixturenames:
    metafunc.parametrize(
      "reference_sample",
      [
        pytest.param(
          reference_sample,
          marks=(
            [pytest.mark.xfail(strict=True)] if reference_sample.known_failure
            else []
          )
        )
        for reference_sample in reference_samples
      ],
      ids=lambda s: (
        f"{s.food.fdc_id}_"
        f"{s.food.description.replace(' ', '_').replace(',', '')}"
      )
    )

def test_categorization(reference_sample):
  category = reference_sample.food.category
  expected_category = reference_sample.expected_category
  assert category == expected_category
