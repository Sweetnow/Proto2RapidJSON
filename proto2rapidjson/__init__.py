#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from .lexer import scan
from .parser import Parser

__all__ = ['lexer', 'scan', 'parser', 'Parser', 'entry']


def set_comment(s: str) -> str:
    """set the indent of each line in `s` `indent`"""
    lines = s.splitlines(False)
    new_lines = []
    for line in lines:
        line = '// ' + line
        new_lines.append(line)
    return '\n'.join(new_lines)+'\n'


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
    parser = Parser(tokens, os.path.splitext(os.path.basename(fin_name))[0])
    with open(fout_name, 'w') as fout:
        fout.write('// ******************************\n')
        fout.write(f'// Origin: {fin_name}\n// Content:\n')
        fout.write(set_comment(s))
        fout.write('// ******************************\n\n')
        fout.write(parser.tocpp())
