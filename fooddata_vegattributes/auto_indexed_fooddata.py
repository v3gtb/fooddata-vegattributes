from contextlib import contextmanager
from logging import getLogger
from os import PathLike
from typing import Callable, Iterable, Union
from tarfile import ReadError as TarFileReadError

from .fooddata import FoodDataDict
from .indexed_fooddata import CompressedIndexedFoodDataJson


logger = getLogger(__name__)

@contextmanager
def auto_compressed_indexed_fooddata_json(
  compressed_indexed_json_path: Union[PathLike, str, bytes],
  load_fooddata_callback: Callable[[], Iterable[FoodDataDict]],
):
  for attempt in range(2):
    try:
      cifj = CompressedIndexedFoodDataJson.from_path(
        compressed_indexed_json_path
      )
      logger.info("indexed JSON archive found")
      break
    except (FileNotFoundError, KeyError, TarFileReadError):
      if attempt > 0:
        raise
      logger.info("indexed JSON archive missing or malformed, (re)generating")
      food_ds = load_fooddata_callback()
      with CompressedIndexedFoodDataJson.from_path(
        compressed_indexed_json_path, "w"
      ) as cifj:
        cifj.write_fooddata_dicts(food_ds)
      logger.info("done writing indexed JSON, trying to load again")
  with cifj:
    yield cifj
