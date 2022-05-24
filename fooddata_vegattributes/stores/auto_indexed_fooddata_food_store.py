from contextlib import contextmanager
from functools import partial
from os import PathLike
from typing import Union

from ..io.auto_indexed_fooddata import auto_compressed_indexed_fooddata_json
from ..io.fooddata import load_survey_fooddata_dicts

from .indexed_fooddata_food_store import IndexedFoodDataFoodStore


@contextmanager
def auto_compressed_indexed_fooddata_food_store(
  compressed_indexed_json_path: Union[PathLike, str, bytes],
  fooddata_json_path: Union[PathLike, str, bytes],
):
  with auto_compressed_indexed_fooddata_json(
    compressed_indexed_json_path=compressed_indexed_json_path,
    load_fooddata_callback=partial(
      load_survey_fooddata_dicts,
      path=fooddata_json_path,
    ),
  ) as cifj:
    with IndexedFoodDataFoodStore(indexed_fooddata_json=cifj) as store:
      yield store
