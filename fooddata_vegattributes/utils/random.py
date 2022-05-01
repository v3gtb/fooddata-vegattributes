import random

def select_n_random(items, n, criterion=None):
  indices_todo = list(range(len(items)))
  selected = []
  while len(selected) < n:
    if not indices_todo:
      if criterion is not None:
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
