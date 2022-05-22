from abc import ABCMeta
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Type, TypeVar


@dataclass
class FileNames:
  survey_fooddata_json: str
  compressed_indexed_fooddata_json: str
  reference_samples_csv: str
  generated_vegattributes_json: str

default_filenames = FileNames(
  survey_fooddata_json=(
    "FoodData_Central_survey_food_json_2021-10-28.json"
  ),
  compressed_indexed_fooddata_json=(
    "indexed_FoodData_Central_survey_food_json_2021-10-28.jsons.tar.xz"
  ),
  reference_samples_csv="reference_samples.csv",
  generated_vegattributes_json=(
    "VegAttributes_for_FoodData_Central_survey_food_json_2021-10-28.json"
  ),
)

@dataclass
class DirRelativePaths:
  """
  Paths relative to some kind of project/work/data/cache directory.
  """
  survey_fooddata_json: Path
  compressed_indexed_fooddata_json: Path
  reference_samples_csv: Path
  generated_vegattributes_json: Path

default_dir_relative_paths = DirRelativePaths(
  survey_fooddata_json=Path(default_filenames.survey_fooddata_json),
  compressed_indexed_fooddata_json=Path(
    default_filenames.compressed_indexed_fooddata_json
  ),
  reference_samples_csv=Path(
    default_filenames.reference_samples_csv
  ),
  generated_vegattributes_json=Path(
    default_filenames.generated_vegattributes_json
  ),
)

T = TypeVar("T")

class AbstractDirPaths(Generic[T], metaclass=ABCMeta):
  dir_path: Path
  dir_relative_paths: T

class CombinedPath:
  def __set_name__(self, owner: AbstractDirPaths, name: str):
    self.name = name

  def __get__(
    self,
    obj: AbstractDirPaths,
    objtype: Type[AbstractDirPaths]=None
  ) -> Path:
    return obj.dir_path/getattr(obj.dir_relative_paths, self.name)

@dataclass
class DirPaths(AbstractDirPaths):
  """
  Paths containing the path to some kind of project/work/data/cache directory.
  """
  dir_path: Path
  dir_relative_paths: DirRelativePaths

  survey_fooddata_json = CombinedPath()
  compressed_indexed_fooddata_json = CombinedPath()
  reference_samples_csv = CombinedPath()
  generated_vegattributes_json = CombinedPath()

default_dir_paths = DirPaths(Path("."), default_dir_relative_paths)
