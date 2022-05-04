from contextlib import contextmanager, ExitStack
from io import BytesIO
import json
from datetime import datetime
from logging import getLogger
from os import PathLike
from pathlib import Path
from tarfile import (
  open as tarfile_open, ReadError as TarFileReadError, TarFile, TarInfo
)
from typing import cast, List, Union

from .fooddata import FoodDataDict, load_survey_fooddata_dicts

logger = getLogger(__name__)

class CompressedIndexedFoodDataJson:
  """
  Compressed, indexed (by FDC ID) FoodData JSON entries stored in a file.
  """
  def __init__(self, tarfile: TarFile):
    self.tarfile = tarfile
    self.close_stack = ExitStack()

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "CompressedIndexedFoodDataJson":
    """
    Opens archive for reading or writing depending on the given mode.

    If mode is `"w"`, we default to using LZMA compression. Use `"w:[method]"`
    for other compression methods and leave `[method]` empty to force no
    compression.
    """
    if mode == "w":
      mode = "w:xz"
    tarfile = tarfile_open(path, mode=mode)
    obj = cls(tarfile=tarfile)
    obj.close_stack.enter_context(tarfile)
    return obj

  def close(self):
    self.close_stack.close()

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    self.close()

  def write_fooddata_dicts(self, ds: List[FoodDataDict]):
    for d in ds:
      fdc_id_str = str(d["fdcId"])
      json_bytes = json.dumps(d).encode("utf-8")
      tar_info = TarInfo(name=fdc_id_str)
      tar_info.size = len(json_bytes)
      tar_info.mtime = int(datetime.now().timestamp())
      self.tarfile.addfile(tar_info, BytesIO(json_bytes))

  def get_fooddata_dict_by_fdc_id(
    self, fdc_id: Union[int, str]
  ) -> FoodDataDict:
    fdc_id_str = str(fdc_id)
    file_for_index = self.tarfile.extractfile(fdc_id_str)
    if file_for_index is None:
      raise KeyError(f"FDC ID {fdc_id} not in indexed JSON file")
    return cast(FoodDataDict, json.load(file_for_index))

@contextmanager
def ensure_compressed_indexed_fooddata_json():
  compressed_indexed_json_path = Path(
    "indexed_FoodData_Central_survey_food_json_2021-10-28.jsons.tar.xz"
  )
  for attempt in range(2):
    try:
      with CompressedIndexedFoodDataJson.from_path(
        compressed_indexed_json_path
      ) as cifj:
        logger.info("indexed JSON archive found")
        yield cifj
      break
    except (FileNotFoundError, KeyError, TarFileReadError):
      if attempt > 0:
        raise
      logger.info("indexed JSON archive missing or malformed, (re)generating")
      food_ds = load_survey_fooddata_dicts()
      with CompressedIndexedFoodDataJson.from_path(
        compressed_indexed_json_path, "w"
      ) as cifj:
        cifj.write_fooddata_dicts(food_ds)
      logger.info("done writing indexed JSON, trying to load again")
