import json
from os import fspath, PathLike
from typing import cast, Generic, Iterable, Tuple, Union
from zipfile import ZipFile, ZIP_DEFLATED

from .abstract_indexed_json import AbstractIndexedJson, T
from .close_via_stack import CloseViaStack


class CompressedIndexedJson(CloseViaStack, AbstractIndexedJson, Generic[T]):
  """
  Compressed, indexed JSON objects stored in a file.
  """
  def __init__(self, zipfile: ZipFile):
    self.zipfile = zipfile

  @classmethod
  def from_path(
    cls,
    path: Union[PathLike, str, bytes],
    mode="r",
    compression=ZIP_DEFLATED,
    compresslevel=None,
  ) -> "CompressedIndexedJson":
    """
    Opens archive for reading or writing depending on the given mode.
    """
    zipfile = ZipFile(
      str(fspath(path)),
      mode=mode,
      compression=compression,
      compresslevel=compresslevel,
    )
    obj = cls(zipfile=zipfile)
    obj.close_stack.enter_context(zipfile)
    return obj

  def write_index_jsonable_tuples(
    self, index_jsonable_tuples: Iterable[Tuple[str, T]]
  ):
    for index, jsonable in index_jsonable_tuples:
      json_bytes = json.dumps(jsonable).encode("utf-8")
      with self.zipfile.open(index, "w") as file_for_index:
        file_for_index.write(json_bytes)

  def get_jsonable_by_index(self, index: str) -> T:
    try:
      with self.zipfile.open(index) as file_for_index:
        return cast(T, json.load(file_for_index))
    except FileNotFoundError as e:
      raise KeyError(f"Entry with key {index} not in indexed JSON file") from e

  def iter_all_indices(self) -> Iterable[str]:
    return (x for x in self.zipfile.namelist())
