import csv
from os import PathLike
from typing import Generator, Iterable, Optional, TypedDict, Union

from .utils.close_on_exit import CloseOnExit
from .utils.close_via_stack import CloseViaStack


class ReferenceSampleDict(TypedDict):
  fdc_id: int
  expected_category: str
  known_failure: bool
  description: Optional[str]

class ReferenceSamplesCsv(CloseViaStack, CloseOnExit):
  """
  CSV file containing reference samples.

  Note that this follows file semantics, meaning there is a cursor and you have
  to be aware of whether a method resets the cursor to the beginning of the
  file before doing anything or not.
  """
  def __init__(
    self,
    file,
    csv_reader: Optional[csv.DictReader]=None,
    csv_writer: Optional[csv.DictWriter]=None,
  ):
    self.file = file
    self.csv_reader = csv_reader
    self.csv_writer = csv_writer

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r+",
  ) -> "ReferenceSamplesCsv":
    """
    Opens CSV file for reading and/or writing depending on the given mode.
    """
    file = open(path, mode)
    csv_reader = None
    csv_writer = None
    if any(m in mode for m in "wa+"):
      csv_writer = csv.DictWriter(
        file,
        ["fdc_id", "expected_category", "known_failure", "description"],
        lineterminator="\n",
      )
    if any(m in mode for m in "r+"):
      csv_reader = csv.DictReader(file)
    if csv_reader is None and csv_writer is None:
      raise ValueError("invalid mode: {repr(mode)}")
    obj = cls(file=file, csv_reader=csv_reader, csv_writer=csv_writer)
    obj.close_stack.enter_context(file)
    return obj

  def reset_and_write_reference_sample_dicts(
    self,
    ds: Iterable[ReferenceSampleDict]
  ):
    self._reset_and_write_header()
    for d in ds:
      self.write_reference_sample_dict(d)

  def write_header_if_empty(self):
    if self._is_empty():
      self._reset_and_write_header()

  def _is_empty(self):
    """Find out if file is empty with minimal cursor changes"""
    is_empty = False
    orig_pos = self.file.tell()
    if not self.file.read(1):
      self.file.seek(0)
      if not self.file.read(1):
        is_empty = True
    self.file.seek(orig_pos)
    return is_empty

  def _reset_and_write_header(self):
    assert self.csv_writer is not None
    self.file.seek(0)
    self.file.truncate()
    self.csv_writer.writeheader()

  def append_reference_sample_dict(self, d: ReferenceSampleDict):
    assert self.csv_writer is not None
    self.file.seek(0, 2)
    self.write_reference_sample_dict(d)

  def write_reference_sample_dict(self, d: ReferenceSampleDict):
    assert self.csv_writer is not None
    self.csv_writer.writerow({
      "fdc_id": d["fdc_id"],
      "expected_category": d["expected_category"],
      "known_failure": "Y" if d["known_failure"] else "N",
      "description": d.get("description"),
    })

  def read_all_reference_sample_dicts(self) \
  -> Generator[ReferenceSampleDict, None, None]:
    """
    Read all reference sample dicts from the beginning to the end of the file.
    """
    assert self.csv_reader is not None
    self.file.seek(0)
    return self.read_reference_sample_dicts()

  def read_reference_sample_dicts(self) \
  -> Generator[ReferenceSampleDict, None, None]:
    """
    Read all following reference sample dicts from the current cursor position.
    """
    assert self.csv_reader is not None
    for row in self.csv_reader:
      yield {
        "fdc_id": int(row["fdc_id"]),
        "expected_category": row["expected_category"],
        "known_failure": row["known_failure"] == "Y",
        "description": row.get("description"),
      }
