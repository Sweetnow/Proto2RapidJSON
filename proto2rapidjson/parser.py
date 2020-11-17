#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from typing import List, NamedTuple
from collections import OrderedDict
from .lexer import TYPE_RESERVED_WORDS, Token, TokenKind

__all__ = ['TokenError', 'ElementKind', 'Element', 'Message', 'Parser']


class TokenError(Exception):
    def __init__(self, token: Token, message: str = 'Unexpected token') -> None:
        self.token = token
        self.message = f'{message} <{token.content}>({token.kind}) in line {token.line}'
        super().__init__(self.message)


class ElementKind(Enum):
    custom = 0
    double = 1
    float = 2
    int32 = 3
    uint32 = 4
    int64 = 5
    uint64 = 6
    bool = 7
    string = 8

    def __str__(self):
        d = {
            ElementKind.double: 'double',
            ElementKind.float: 'float',
            ElementKind.int32: 'int32_t',
            ElementKind.uint32: 'uint32_t',
            ElementKind.int64: 'int64_t',
            ElementKind.uint64: 'uint64_t',
            ElementKind.bool: 'bool',
            ElementKind.string: 'const char *'
        }
        return d[self]


class Element(NamedTuple):
    identifier: str
    kind: ElementKind
    kindstr: str
    repeated: bool

    def to_declaration(self) -> str:
        if self.repeated:
            return f'std::vector<{self.kindstr}> {self.identifier};\n'
        else:
            return f'{self.kindstr} {self.identifier};\n'

    def to_get(self) -> str:
        if self.repeated:
            base = 'i'
        else:
            base = f'v["{self.identifier}"]'
        check_function = {
            ElementKind.double: f'{base}.IsDouble()',
            ElementKind.float: f'{base}.IsFloat()',
            ElementKind.int32: f'{base}.IsInt()',
            ElementKind.uint32: f'{base}.IsUint()',
            ElementKind.int64: f'{base}.IsInt64()',
            ElementKind.uint64: f'{base}.IsUint64()',
            ElementKind.bool: f'{base}.IsBool()',
            ElementKind.string: f'{base}.IsString()',
            ElementKind.custom: f'{base}.IsObject()'
        }
        get_function = {
            ElementKind.double: f'{base}.GetDouble()',
            ElementKind.float: f'{base}.GetFloat()',
            ElementKind.int32: f'{base}.GetInt()',
            ElementKind.uint32: f'{base}.GetUint()',
            ElementKind.int64: f'{base}.GetInt64()',
            ElementKind.uint64: f'{base}.GetUint64()',
            ElementKind.bool: f'{base}.GetBool()',
            ElementKind.string: f'{base}.GetString()',
            ElementKind.custom: f'{self.kindstr}().Get({base})'
        }

        if self.repeated:
            return f'''//parse {self.identifier}
assert(v.HasMember("{self.identifier}"));
assert(v["{self.identifier}"].IsArray());
for (auto&& i : v["{self.identifier}"].GetArray()) {{
    assert({check_function[self.kind]});
    {self.identifier}.emplace_back({get_function[self.kind]});
}}
'''
        else:
            return f'''//parse {self.identifier}
assert(v.HasMember("{self.identifier}"));
assert({check_function[self.kind]});
{self.identifier} = {get_function[self.kind]};
'''


class Message(NamedTuple):
    identifier: str
    elements: List[Element]

    def to_struct(self) -> str:
        body = []
        for lines in [e.to_get().splitlines(False) for e in self.elements]:
            body += lines
        body = '\n        '.join(body)
        return f'''struct {self.identifier} {{
    {'    '.join(e.to_declaration() for e in self.elements)}
    {self.identifier}& Parse(const char* str) {{
        rapidjson::Document document;
        document.Parse(str);
        assert(document.IsObject());
        return Get(document);
    }}
    {self.identifier}& Get(const rapidjson::Value& v) {{
        {body}
        return *this;
    }}
}};
'''


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.package: str
        self.messages = OrderedDict()
        self.parse()

    def try_match_reserved(self, word: str) -> bool:
        token = self.tokens[0]
        if token.kind == TokenKind.RESERVED and token.content == word:
            self.tokens = self.tokens[1:]
            return True
        else:
            return False

    def match_reserved(self, word: str) -> None:
        token = self.tokens[0]
        if token.kind == TokenKind.RESERVED and token.content == word:
            self.tokens = self.tokens[1:]
        else:
            raise TokenError(token)

    def try_match_eof(self) -> bool:
        token = self.tokens[0]
        if token.kind == TokenKind.EOF:
            self.tokens = self.tokens[1:]
            return True
        else:
            return False

    def match_identifier(self) -> str:
        token = self.tokens[0]
        if token.kind == TokenKind.IDENTIDIER:
            self.tokens = self.tokens[1:]
            return token.content
        else:
            raise TokenError(token)

    def match_number(self) -> int:
        token = self.tokens[0]
        if token.kind == TokenKind.NUMBER:
            self.tokens = self.tokens[1:]
            return int(token.content)
        else:
            raise TokenError(token)

    def parse_element(self) -> Element:
        repeated = self.try_match_reserved('repeated')
        type_token = self.tokens[0]
        if type_token.kind == TokenKind.IDENTIDIER and type_token.content in self.messages:
            kind = ElementKind.custom
            kindstr = type_token.content
        elif type_token.kind == TokenKind.RESERVED and type_token.content in TYPE_RESERVED_WORDS:
            kind = ElementKind[type_token.content]
            kindstr = str(kind)
        else:
            raise TokenError(type_token, 'Unknown type')
        self.tokens = self.tokens[1:]
        identifier = self.match_identifier()
        # only for compatibility
        if self.try_match_reserved('='):
            self.match_number()
        self.match_reserved(';')
        return Element(identifier, kind, kindstr, repeated)

    def parse_message(self) -> None:
        self.match_reserved('message')
        identifier = self.match_identifier()
        message = Message(identifier, [])
        self.match_reserved('{')
        while not self.try_match_reserved('}'):
            message.elements.append(self.parse_element())
        self.messages[identifier] = message

    def parse_package(self) -> None:
        self.match_reserved('package')
        self.package = self.match_identifier()
        self.match_reserved(';')

    def parse(self) -> None:
        self.parse_package()
        self.parse_message()
        while not self.try_match_eof():
            self.parse_message()

    def tocpp(self) -> str:
        return f'''#ifndef _PROTO2RAPIDJSON_{self.package.upper()}_HEADER_
#define _PROTO2RAPIDJSON_{self.package.upper()}_HEADER_

// Generated by Proto2RapidJSON
// https://github.com/Sweetnow/proto2rapidjson

#include <vector>

#include "rapidjson/document.h"

namespace {self.package} {{
{''.join(m.to_struct() for m in self.messages.values())}
}}  // namespace {self.package}
#endif
'''
