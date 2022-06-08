from argparse import ArgumentParser

from ..category import Category

from .annotate_reference_samples import main as annotate_ref_main
from .generate import main as generate_main
from .input_reference_samples import main as input_ref_main
from .list_by_veg_and_fdc_categories import (
  main as list_by_veg_and_fdc_categories_main
)


def annotate_ref():
  return annotate_ref_main()

def input_ref():
  return input_ref_main()

def generate():
  return generate_main()

def list_by_veg_and_fdc_categories(
  fdc_category_description: str,
  veg_category: str
):
  return list_by_veg_and_fdc_categories_main(
    fdc_category_description,
    Category[veg_category],
  )


def main():
  parser = ArgumentParser(prog="fooddata-vegattributes")
  subparsers = parser.add_subparsers()

  # "generate" subcommand
  generate_parser = subparsers.add_parser(
    "generate",
    help="generate vegattributes JSON"
  )
  generate_parser.set_defaults(func=generate)

  # "input-ref" subcommand
  input_ref_parser = subparsers.add_parser(
    "input-ref",
    help="interactively input reference data"
  )
  input_ref_parser.set_defaults(func=input_ref)

  # "annotate-ref" subcommand
  annotate_ref_parser = subparsers.add_parser(
    "annotate-ref",
    help="annotate reference data"
  )
  annotate_ref_parser.set_defaults(func=annotate_ref)

  # "list-by-veg-and-fdc-categories" subcommand
  list_by_categories_parser = subparsers.add_parser(
    "list-by-veg-and-fdc-categories",
    help="list foods by veg and FDC categories"
  )
  list_by_categories_parser.set_defaults(func=list_by_veg_and_fdc_categories)
  list_by_categories_parser.add_argument(
    "--fdc-category-description", required=True
  )
  list_by_categories_parser.add_argument("--veg-category", required=True)


  args = parser.parse_args()
  args.func(**{k: v for k, v in vars(args).items() if k != "func"})

  parser.exit()
