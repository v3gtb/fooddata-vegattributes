from abc import ABCMeta, abstractmethod
from typing import Iterable, Union

from .fooddata import FoodDataDict
from .utils.abstract_indexed_json import AbstractIndexedJson


class AbstractIndexedFoodDataJson(metaclass=ABCMeta):
  indexed_json: AbstractIndexedJson

  @abstractmethod
  def close(self): ...

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    self.close()

  def write_fooddata_dicts(self, ds: Iterable[FoodDataDict]):
    self.indexed_json.write_index_jsonable_tuples(
      (str(d["fdcId"]), d) for d in ds
    )

  def get_fooddata_dict_by_fdc_id(
    self, fdc_id: Union[int, str]
  ) -> FoodDataDict:
    return self.indexed_json.get_jsonable_by_index(str(fdc_id))

  def get_all_fdc_ids(self) -> Iterable[int]:
    return [int(x) for x in self.indexed_json.iter_all_indices()]
