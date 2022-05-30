from .with_default_paths import default_food_and_reference_sample_stores


def main():
  with default_food_and_reference_sample_stores() as (
    food_store, reference_sample_store
  ):
    # simply read them out and write them back, the store automatically
    # annotates with descriptions on write
    reference_samples = list(reference_sample_store.iter_all())
    reference_sample_store.reset_and_put_all(reference_samples)
