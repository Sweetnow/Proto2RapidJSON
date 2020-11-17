#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from . import entry

__all__ = ['entry']


def get_argparser() -> ArgumentParser:
    parser = ArgumentParser(
        'proto2rapidjson', description='Convert .proto file to header-only RapidJSON based c++ code')
    parser.add_argument('-i', '--input', type=str, dest='input',
                        help='input .proto file', required=True)
    parser.add_argument('-o', '--output', type=str, dest='output',
                        help='output .h file', required=True)
    parser.add_argument('-y', dest='yes', action='store_true',
                        help='pass all interactive checks', default=False)
    return parser


def main():
    args = get_argparser().parse_args()
    entry(args.input, args.output, args.yes)


if __name__ == "__main__":
    main()
