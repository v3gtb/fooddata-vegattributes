from contextlib import ExitStack
from io import BytesIO
import json
from datetime import datetime
from os import PathLike
from tarfile import (
  open as tarfile_open, TarFile, TarInfo
)
from typing import cast, Generic, Iterable, Tuple, Union

from .abstract_indexed_json import AbstractIndexedJson, T


class CompressedIndexedJson(AbstractIndexedJson, Generic[T]):
  """
  Compressed, indexed JSON objects stored in a file.
  """
  def __init__(self, tarfile: TarFile):
    self.tarfile = tarfile
    self.close_stack = ExitStack()

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "CompressedIndexedJson":
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

  def write_index_jsonable_tuples(
    self, index_jsonable_tuples: Iterable[Tuple[str, T]]
  ):
    for index, jsonable in index_jsonable_tuples:
      json_bytes = json.dumps(jsonable).encode("utf-8")
      tar_info = TarInfo(name=index)
      tar_info.size = len(json_bytes)
      tar_info.mtime = int(datetime.now().timestamp())
      self.tarfile.addfile(tar_info, BytesIO(json_bytes))

  def get_jsonable_by_index(self, index: str) -> T:
    file_for_index = self.tarfile.extractfile(index)
    if file_for_index is None:
      raise KeyError(f"Entry with key {index} not in indexed JSON file")
    return cast(T, json.load(file_for_index))

  def iter_all_indices(self) -> Iterable[str]:
    return (x for x in self.tarfile.getnames())
