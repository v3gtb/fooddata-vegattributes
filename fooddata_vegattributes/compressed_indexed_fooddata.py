from os import PathLike
from typing import Union

from .abstract_indexed_fooddata import AbstractIndexedFoodDataJson
from .fooddata import FoodDataDict
from .utils.indexed_jsonable_store import IndexedJsonableStore, IndexSpec
from .utils.close_via_stack import CloseViaStack


class CompressedIndexedFoodDataJson(CloseViaStack, AbstractIndexedFoodDataJson):
  """
  Compressed, indexed (by FDC ID) FoodData JSON entries stored in a file.
  """
  def __init__(
    self, compressed_indexed_json: IndexedJsonableStore[FoodDataDict]
  ):
    self.indexed_json = compressed_indexed_json

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "CompressedIndexedFoodDataJson":
    """
    Opens archive for reading or writing depending on the given mode.

    See `CompressedIndexedJson` docs for possible modes.
    """
    compressed_indexed_json = IndexedJsonableStore.from_path(
      path,
      primary_index=IndexSpec("fdc-id", lambda d: str(d["fdcId"])),
      secondary_indices=[
        IndexSpec(
          "ingredient-code",
          lambda d: str(d.get("foodCode") or d.get("ndbNumber")),
        ),
        IndexSpec(
          "fdc-category-description",
          lambda d: (
            d.get("wweiaFoodCategory", {}).get("wweiaFoodCategoryDescription")
            or d.get("foodCategory", {}).get("description")
          ),
        ),
      ],
      mode=mode,
    )
    obj = cls(compressed_indexed_json=compressed_indexed_json)
    obj.close_stack.enter_context(compressed_indexed_json)
    return obj
