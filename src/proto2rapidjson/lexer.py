#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, NamedTuple
from enum import Enum

__all__ = ['TYPE_RESERVED_WORDS',
           'RESERVED_WORDS', 'TokenKind', 'Token', 'scan']


TYPE_RESERVED_WORDS = ['double', 'float', 'int32',
                       'uint32', 'int64', 'uint64', 'bool', 'string']
RESERVED_WORDS = ['message', 'package',
                  '{', '}', ';', 'repeated', '//', '='] + TYPE_RESERVED_WORDS


class TokenKind(Enum):
    RESERVED = 0
    IDENTIDIER = 1
    NUMBER = 2
    EOF = 3


class Token(NamedTuple):
    content: str
    kind: TokenKind
    line: int


def scan(input: str) -> List[Token]:
    tokens: List[Token] = []
    for i, line in enumerate(input.splitlines(False)):
        line = line.strip()
        while(len(line) > 0):
            # scan reserved words
            reserved = False
            for word in RESERVED_WORDS:
                if line.startswith(word):
                    if word == '//':
                        line = ''
                    else:
                        tokens.append(Token(word, TokenKind.RESERVED, i+1))
                        line = line[len(word):]
                    reserved = True
                    break
            if reserved:
                line = line.strip()
                continue
            # scan identifier
            identifier = ''
            for c in line:
                if identifier == '' and c.isalpha() or identifier != '' and c.isalnum():
                    identifier += c
                else:
                    break
            if identifier != '':
                line = line[len(identifier):]
                tokens.append(Token(identifier, TokenKind.IDENTIDIER, i+1))
                line = line.strip()
                continue
            # scan number
            number = ''
            for c in line:
                if c.isdigit():
                    number += c
                else:
                    break
            if number != '':
                line = line[len(number):]
                tokens.append(Token(number, TokenKind.NUMBER, i+1))
                number = int(number)
                line = line.strip()
                continue
            # report error
            raise ValueError(f"invalid input: {line}")

    tokens.append(Token('', TokenKind.EOF, -1))
    return tokens
