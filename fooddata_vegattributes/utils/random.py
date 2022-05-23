import random
from typing import Callable, List, Optional, Sequence, TypeVar


T = TypeVar("T")

def select_n_random(
  items: Sequence[T],
  n: int,
  criterion: Optional[Callable[[T], bool]]=None,
  pad: Optional[Callable[[], T]]=None,
) -> List[T]:
  indices_todo = list(range(len(items)))
  selected: List[T] = []
  while len(selected) < n:
    if not indices_todo:
      if pad:
        selected.extend(pad() for _ in range(n-len(selected)))
        break
      else:
        error_msg = (
          "not enough items fulfilling criterion in given sequence"
          if criterion is not None else "not enough items in given sequence"
        )
        raise ValueError(error_msg)
    i = random.choice(indices_todo)
    indices_todo.remove(i)
    item = items[i]
    if criterion is not None and not criterion(item):
      continue
    else:
      selected.append(item)
  return selected
