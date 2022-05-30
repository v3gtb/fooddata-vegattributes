from contextlib import contextmanager
from functools import partial
from os import PathLike
from typing import List, Union

from .auto_indexed_fooddata import auto_compressed_indexed_fooddata_json
from .fooddata import (
  FoodDataDict,
  load_sr_legacy_fooddata_dicts,
  load_survey_fooddata_dicts,
)
from .indexed_fooddata_food_store import IndexedFoodDataFoodStore


def load_all_fooddata_dicts(
  survey_fooddata_json_path: Union[PathLike, str, bytes],
  sr_legacy_fooddata_json_path: Union[PathLike, str, bytes],
) -> List[FoodDataDict]:
  l = load_survey_fooddata_dicts(survey_fooddata_json_path)
  l.extend(load_sr_legacy_fooddata_dicts(sr_legacy_fooddata_json_path))
  return l

@contextmanager
def auto_compressed_indexed_fooddata_food_store(
  compressed_indexed_json_path: Union[PathLike, str, bytes],
  survey_fooddata_json_path: Union[PathLike, str, bytes],
  sr_legacy_fooddata_json_path: Union[PathLike, str, bytes],
):
  with auto_compressed_indexed_fooddata_json(
    compressed_indexed_json_path=compressed_indexed_json_path,
    load_fooddata_callback=partial(
      load_all_fooddata_dicts,
      survey_fooddata_json_path=survey_fooddata_json_path,
      sr_legacy_fooddata_json_path=sr_legacy_fooddata_json_path,
    ),
  ) as cifj:
    with IndexedFoodDataFoodStore(indexed_fooddata_json=cifj) as store:
      yield store
