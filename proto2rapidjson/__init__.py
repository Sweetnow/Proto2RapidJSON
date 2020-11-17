#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from .lexer import scan
from .parser import Parser

__all__ = ['lexer', 'scan', 'parser', 'Parser', 'entry']


def entry(fin_name: str, fout_name: str, overwrite: bool) -> None:
    with open(fin_name, 'r') as fin:
        s = fin.read()
    if os.path.exists(fout_name) and not overwrite:
        check = input(
            f'File {fout_name} is existed, do you want to overwrite it? [y/N]')
        if check.lower() == 'y' or check == '':
            pass
        else:
            return
    tokens = scan(s)
    parser = Parser(tokens)
    with open(fout_name, 'w') as fout:
        fout.write(parser.tocpp())
