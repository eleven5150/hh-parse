import argparse
import sys

from resumes import resumes_subparser
from vacancies import vacancies_subparser


def parse_args(arguments: list):
    parser = argparse.ArgumentParser(description="hh-parse - tool for parsing hh.ru")

    subparsers = parser.add_subparsers(
        required=True,
        title="tools",
        help="Tool to use",
        dest="tool",
    )

    vacancies_subparser(subparsers)
    resumes_subparser(subparsers)

    return parser.parse_args(arguments)


def main(raw_arguments: list) -> None:
    args = parse_args(raw_arguments[1:])
    print(f"Starting {args.tool}")
    args.func(args)



if __name__ == '__main__':
    main(sys.argv)
