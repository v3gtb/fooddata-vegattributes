from argparse import ArgumentParser

from .annotate_reference_samples import main as annotate_ref_main
from .generate import main as generate_main
from .input_reference_samples import main as input_ref_main


def annotate_ref():
  return annotate_ref_main()

def input_ref():
  return input_ref_main()

def generate():
  return generate_main()

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

  args = parser.parse_args()
  args.func(**{k: v for k, v in vars(args).items() if k != "func"})

if __name__ == "__main__":
  main()
