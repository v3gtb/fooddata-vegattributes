import json
from os import fspath, PathLike
from pathlib import Path
from typing import cast, Generator, Generic, Iterable, Tuple, Union
from zipfile import ZipFile, ZIP_DEFLATED

from .abstract_indexed_json import (
  AbstractIndexedJson,
  LinkTargets,
  LinksForSourceIndexName,
  T,
)
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

  def write_jsonables(
    self, index_name: str, index_values_and_jsonables: Iterable[Tuple[str, T]]
  ):
    for index_value, jsonable in index_values_and_jsonables:
      json_bytes = json.dumps(jsonable).encode("utf-8")
      path_in_zip = f"by-{index_name}/data/{index_value}"
      with self.zipfile.open(path_in_zip, "w") as file_in_zip:
        file_in_zip.write(json_bytes)

  def write_links(
    self,
    index_name: str,
    index_values_and_targets: Iterable[Tuple[str, LinkTargets]]
  ):
    try:
      links_for_index = self._load_links(index_name)
    except KeyError:
      links_for_index = {}
    links_for_index.update(index_values_and_targets)
    self._write_links(index_name, links_for_index)

  def get_jsonables(
    self, index_name: str, index_value: str
  ) -> Generator[T, None, None]:
    for index_name, index_value in self._resolve(index_name, index_value):
      yield self._get_jsonable_no_resolve(index_name, index_value)

  def get_jsonable(self, index_name: str, index_value: str) -> T:
    jsonables_iter = self.get_jsonables(index_name, index_value)
    try:
      result = next(jsonables_iter)
    except StopIteration as e:
      raise KeyError(f"no entry found for {index_name}={index_value}") from e
    try:
      next(jsonables_iter)
    except StopIteration:
      pass
    else:
      raise ValueError(f"more than one result for {index_name}={index_value}")
    return result

  def _get_jsonable_no_resolve(self, index_name: str, index_value: str) -> T:
    try:
      path_in_zip = f"by-{index_name}/data/{index_value}"
      with self.zipfile.open(path_in_zip) as file_in_zip:
        jsonable = cast(T, json.load(file_in_zip))
      return jsonable
    except KeyError as e:
      raise KeyError(
        f"Entry for {index_name}={index_value} not in indexed JSON file"
      ) from e

  def iter_index(self, index_name: str) -> Iterable[str]:
    if self._is_data_index(index_name):
      return self._iter_data_index(index_name)
    else:
      return self._load_links(index_name).keys()

  def _iter_data_index(self, index_name: str) -> Iterable[str]:
    return (
      Path(x).name for x in self.zipfile.namelist()
      if x.startswith(f"by-{index_name}/data/")
    )

  def _is_data_index(self, index_name: str) -> bool:
    return any(
      x.startswith(f"by-{index_name}/data/")
      for x in self.zipfile.namelist()
    )

  def _is_link_index(self, index_name: str) -> bool:
    return any(
      x.startswith(f"by-{index_name}/links.json")
      for x in self.zipfile.namelist()
    )

  def _load_links(self, index_name: str) -> LinksForSourceIndexName:
    with self.zipfile.open("by-{index_name}/links.json") as links_file:
      return json.load(links_file)

  def _write_links(
    self,
    index_name: str,
    links_for_index: LinksForSourceIndexName,
  ):
    json_bytes = json.dumps(links_for_index).encode("utf-8")
    with self.zipfile.open("by-{index_name}/links.json", "w") as links_file:
      links_file.write(json_bytes)

  def _resolve(
    self, index_name: str, index_value: str
  ) -> Iterable[Tuple[str, str]]:
    if self._is_data_index(index_name) or not self._is_link_index(index_name):
      yield (index_name, index_value)
      return
    links_for_index = self._load_links(index_name)
    for target in links_for_index[index_value]:
      for resolved_target in self._resolve(*target):
        yield resolved_target
