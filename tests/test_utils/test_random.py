from fooddata_vegattributes.utils.random import select_n_random


def test_select_n_random():
  n = 10
  l = list(range(100))
  selected = select_n_random(l, n)
  assert len(selected) == n
  assert len(set(selected)) == n
  assert all(s in l for s in selected)

def test_select_n_random_with_criterion():
  n = 10
  l = list(range(100))
  criterion = lambda x: x<20
  selected = select_n_random(l, n, criterion=criterion)
  assert len(selected) == n
  assert len(set(selected)) == n
  assert all(s in l for s in selected)
  assert all(criterion(s) for s in selected)
