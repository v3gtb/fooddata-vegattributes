import os
from textwrap import wrap

from .general import one

def print_as_table(rows, column_width=None):
  try:
    terminal_width = os.get_terminal_size().columns
  except OSError:
    terminal_width = 80
  n_columns_set = set(len(row) for row in rows)
  n_columns = one(n_columns_set)
  if column_width is None:
    column_width = terminal_width // n_columns - 1
  print("+".join("-"*column_width for _ in range(n_columns)))
  for row in rows:
    output_rows = []
    for i, column in enumerate(row):
      wrapped_rows = wrap(column, width=column_width)
      for _ in range(max(0, len(wrapped_rows)-len(output_rows))):
        output_rows.append(["" for _ in range(n_columns)])
      for j, wrapped_row in enumerate(wrapped_rows):
        output_rows[j][i] = wrapped_row
    for output_row in output_rows:
      print("|".join(
        "{{output_cell:<{w}}}"
        .format(w=column_width)
        .format(output_cell=output_cell)
        for output_cell in output_row
      ))
    print("+".join("-"*column_width for _ in range(n_columns)))
