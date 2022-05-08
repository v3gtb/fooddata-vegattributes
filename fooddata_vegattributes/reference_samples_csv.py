from contextlib import ExitStack
import csv
from os import PathLike
from typing import Generator, Optional, TypedDict, Union


class ReferenceSampleDict(TypedDict):
  fdc_id: int
  expected_category: str
  known_failure: bool
  description: Optional[str]

class ReferenceSamplesCsv:
  """
  CSV file containing reference samples.
  """
  def __init__(self, file, csv_io: Union[csv.DictWriter, csv.DictReader]):
    self.file = file
    self.close_stack = ExitStack()
    self.csv_io = csv_io

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "ReferenceSamplesCsv":
    """
    Opens CSV file for reading or writing depending on the given mode.
    """
    file = open(path, mode)
    csv_io: Union[csv.DictWriter, csv.DictReader]
    if mode == "w" or mode == "a":
      csv_io = csv.DictWriter(
        file,
        ["fdc_id", "expected_category", "known_failure", "description"],
        lineterminator="\n",
      )
      if mode != "a":
        csv_io.writeheader()
    elif mode == "r":
      csv_io = csv.DictReader(file)
    else:
      raise ValueError("mode must be one of 'r', or 'w' or 'a'")
    obj = cls(file=file, csv_io=csv_io)
    obj.close_stack.enter_context(file)
    return obj

  def close(self):
    self.close_stack.close()

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    self.close()

  def write_reference_sample_dict(self, d: ReferenceSampleDict):
    assert isinstance(self.csv_io, csv.DictWriter)
    self.csv_io.writerow({
      "fdc_id": d["fdc_id"],
      "expected_category": d["expected_category"],
      "known_failure": "Y" if d["known_failure"] else "N",
      "description": d.get("description"),
    })

  def get_reference_sample_dicts(self) \
  -> Generator[ReferenceSampleDict, None, None]:
    assert isinstance(self.csv_io, csv.DictReader)
    for row in self.csv_io:
      yield {
        "fdc_id": int(row["fdc_id"]),
        "expected_category": row["expected_category"],
        "known_failure": row["known_failure"] == "Y",
        "description": row.get("description"),
      }
