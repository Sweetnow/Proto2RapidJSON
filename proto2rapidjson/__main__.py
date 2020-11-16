#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from argparse import ArgumentParser
from . import scan, Parser


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
    with open(args.input, 'r') as fin:
        s = fin.read()
    if os.path.exists(args.output):
        if not args.yes:
            check = input(
                f'File {args.output} is existed, do you want to overwrite it? [y/N]')
            if check.lower() == 'y' or check == '':
                pass
            else:
                exit(0)
    tokens = scan(s)
    parser = Parser(tokens)
    with open(args.output, 'w') as fout:
        fout.write(parser.tocpp())

if __name__ == "__main__":
    main()