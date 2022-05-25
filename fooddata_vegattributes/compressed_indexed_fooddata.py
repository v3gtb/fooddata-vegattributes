from contextlib import ExitStack
from os import PathLike
from typing import Union

from .abstract_indexed_fooddata import AbstractIndexedFoodDataJson
from .fooddata import FoodDataDict
from .utils.compressed_indexed_json import CompressedIndexedJson


class CompressedIndexedFoodDataJson(AbstractIndexedFoodDataJson):
  """
  Compressed, indexed (by FDC ID) FoodData JSON entries stored in a file.
  """
  def __init__(
    self, compressed_indexed_json: CompressedIndexedJson[FoodDataDict]
  ):
    self.indexed_json = compressed_indexed_json
    self.close_stack = ExitStack()

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "CompressedIndexedFoodDataJson":
    """
    Opens archive for reading or writing depending on the given mode.

    See `CompressedIndexedJson` docs for possible modes.
    """
    compressed_indexed_json = CompressedIndexedJson.from_path(path, mode)
    obj = cls(compressed_indexed_json=compressed_indexed_json)
    obj.close_stack.enter_context(compressed_indexed_json)
    return obj

  def close(self):
    self.close_stack.close()
