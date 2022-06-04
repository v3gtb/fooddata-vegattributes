import json
from os import fspath, PathLike
from pathlib import Path
from typing import cast, Dict, Generic, Iterable, Tuple, Union
from zipfile import ZipFile, ZIP_DEFLATED

from .abstract_indexed_json import AbstractIndexedJson, T
from .close_via_stack import CloseViaStack


Link = Tuple[str, str]
LinksForSourceIndexName = Dict[str, Link]
Links = Dict[str, LinksForSourceIndexName]

class CompressedIndexedJson(CloseViaStack, AbstractIndexedJson, Generic[T]):
  """
  Compressed, indexed JSON objects stored in a file.
  """
  def __init__(self, zipfile: ZipFile):
    self.zipfile = zipfile

    # manual caching
    self._links: Links = {}

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

  def close(self):
    super().close()

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
    index_values_and_targets: Iterable[Tuple[str, Tuple[str, str]]]
  ):
    try:
      links_for_index = self._load_links(index_name)
    except KeyError:
      links_for_index = {}
    links_for_index.update(index_values_and_targets)
    self._write_links(index_name, links_for_index)

  def get_jsonable(self, index_name: str, index_value: str) -> T:
    index_name, index_value = self._resolve(index_name, index_value)
    try:
      path_in_zip = f"by-{index_name}/data/{index_value}"
      with self.zipfile.open(path_in_zip) as file_in_zip:
        return cast(T, json.load(file_in_zip))
    except KeyError as e:
      raise KeyError(
        f"Entry for {index_name}={index_value} not in indexed JSON file"
      ) from e

  def iter_index(self, index_name: str) -> Iterable[str]:
    if self._is_data_index(index_name):
      return (
        Path(x).name for x in self.zipfile.namelist()
        if x.startswith(f"by-{index_name}/data/")
      )
    else:
      return self._load_links(index_name).keys()

  def _is_data_index(self, index_name: str):
    return any(
      x.startswith(f"by-{index_name}/data/")
      for x in self.zipfile.namelist()
    )

  def _is_link_index(self, index_name: str):
    return any(
      x.startswith(f"by-{index_name}/links.json")
      for x in self.zipfile.namelist()
    )

  def _load_links(self, index_name: str) -> LinksForSourceIndexName:
    if index_name not in self._links:
      with self.zipfile.open("by-{index_name}/links.json") as links_file:
        self._links[index_name] = json.load(links_file)
    return self._links[index_name]

  def _write_links(
    self,
    index_name: str,
    links_for_index: LinksForSourceIndexName,
  ):
    json_bytes = json.dumps(links_for_index).encode("utf-8")
    with self.zipfile.open("by-{index_name}/links.json", "w") as links_file:
      links_file.write(json_bytes)
      self._links[index_name] = links_for_index

  def _resolve(self, index_name: str, index_value: str) -> Tuple[str, str]:
    if self._is_data_index(index_name) or not self._is_link_index(index_name):
      return index_name, index_value
    links_for_index = self._load_links(index_name)
    return self._resolve(*links_for_index[index_value])
