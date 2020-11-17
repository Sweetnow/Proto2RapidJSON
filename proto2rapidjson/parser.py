#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from typing import List, NamedTuple
try:
    from typing import OrderedDict
    OrderedDictType = OrderedDict
except ImportError:
    from typing import MutableMapping
    from collections import OrderedDict
    OrderedDictType = MutableMapping
from .lexer import TYPE_RESERVED_WORDS, Token, TokenKind

__all__ = ['TokenError', 'ElementKind', 'Element', 'Message', 'Parser']


class TokenError(Exception):
    def __init__(self, token: Token, message: str = 'Unexpected token') -> None:
        self.token = token
        self.message = f'{message} <{token.content}>({token.kind}) in line {token.line}'
        super().__init__(self.message)


API_NAME = {
    'parse_entry': 'FromString',
    'parse_worker': 'FromValue',
    'stringify_entry': 'ToString',
    'stringify_worker': 'ToValue',
    'pretty_stringify_entry': 'ToPrettyString'
}


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
            ElementKind.string: 'std::string'
        }
        return d[self]


def set_indent(s: str, indent: int, newline: bool) -> str:
    """set the indent of each line in `s` `indent`"""
    lines = s.splitlines(False)
    new_lines = []
    for line in lines:
        line = ' '*indent + line
        new_lines.append(line)
    return '\n'.join(new_lines)+('\n' if newline else '')


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

    def to_parse(self) -> str:
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
            ElementKind.custom: f'{self.kindstr}().{API_NAME["parse_worker"]}({base})'
        }

        if self.repeated:
            return f'''// parse {self.identifier}
assert(v.HasMember("{self.identifier}"));
assert(v["{self.identifier}"].IsArray());
for (auto&& i : v["{self.identifier}"].GetArray()) {{
    assert({check_function[self.kind]});
    {self.identifier}.emplace_back({get_function[self.kind]});
}}
'''
        else:
            return f'''// parse {self.identifier}
assert(v.HasMember("{self.identifier}"));
assert({check_function[self.kind]});
{self.identifier} = {get_function[self.kind]};
'''

    def to_stringify(self) -> str:
        if self.repeated:
            base = 'i'
        else:
            base = self.identifier
        if self.kind == ElementKind.custom:
            body = f'{base}.ToValue(allocator)'
        else:
            body = f'{base}'
        if self.repeated:
            return f'''// stringify {self.identifier}
a.SetArray();
for (auto&& i : {self.identifier}) {{
    a.PushBack({body}, allocator);
}}
v.AddMember("{self.identifier}", a, allocator);
'''
        else:
            return f'''// stringify {self.identifier}
v.AddMember("{self.identifier}", {body}, allocator);
'''


class Message(NamedTuple):
    identifier: str
    elements: OrderedDictType[str, Element]

    def to_struct(self) -> str:
        define_variable = f'{set_indent("".join(e.to_declaration() for e in self.elements.values()), 4, True)}'
        parse_entry = \
            f'''    {self.identifier}& {API_NAME["parse_entry"]}(const char* str) {{
        rapidjson::Document document;
        document.Parse(str);
        assert(document.IsObject());
        return {API_NAME["parse_worker"]}(document);
    }}
'''
        parse_worker = \
            f'''    {self.identifier}& {API_NAME["parse_worker"]}(const rapidjson::Value& v) {{
{set_indent(''.join(e.to_parse() for e in self.elements.values()), 8, False)}
        return *this;
    }}
'''
        stringify_entry = \
            f'''    std::string {API_NAME["stringify_entry"]}() {{
        rapidjson::Document document;
        document.SetObject() = {API_NAME["stringify_worker"]}(document.GetAllocator());
        rapidjson::StringBuffer buffer;
        rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
        document.Accept(writer);
        return buffer.GetString();
    }}
'''

        pretty_stringify_entry = \
            f'''    std::string {API_NAME["pretty_stringify_entry"]}() {{
        rapidjson::Document document;
        document.SetObject() = {API_NAME["stringify_worker"]}(document.GetAllocator());
        rapidjson::StringBuffer buffer;
        rapidjson::PrettyWriter<rapidjson::StringBuffer> writer(buffer);
        document.Accept(writer);
        return buffer.GetString();
    }}
'''

        anylist = any(e.repeated for e in self.elements.values())
        arraystr = 'rapidjson::Value a;\n' if anylist else ''
        stringify_worker = \
            f'''    rapidjson::Value ToValue(rapidjson::Document::AllocatorType& allocator) {{
        rapidjson::Value v(rapidjson::kObjectType);
        {arraystr}
{set_indent(''.join(e.to_stringify() for e in self.elements.values()), 8, False)}
        return v;
    }}
'''

        return f'''struct {self.identifier} {{
{define_variable}
{parse_entry}
{parse_worker}
{stringify_entry}
{pretty_stringify_entry}
{stringify_worker}
}};
'''


class Parser:
    def __init__(self, tokens: List[Token], unique_macro: str) -> None:
        self.tokens = tokens
        self.unique_macro = unique_macro
        self.package: str
        self.messages: OrderedDictType[str, Message] = OrderedDict()
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
        message = Message(identifier, OrderedDict())
        self.match_reserved('{')
        while not self.try_match_reserved('}'):
            element = self.parse_element()
            if element.identifier in message.elements:
                raise KeyError(
                    f'Element {element.identifier} is defined repeatedly')
            else:
                message.elements[element.identifier] = element
        if identifier in self.messages:
            raise KeyError(f'Message {identifier} is defined repeatedly')
        else:
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
        return f'''#ifndef _PROTO2RAPIDJSON_{self.unique_macro.upper()}_{self.package.upper()}_HEADER_
#define _PROTO2RAPIDJSON_{self.unique_macro.upper()}_{self.package.upper()}_HEADER_

// Generated by Proto2RapidJSON
// https://github.com/Sweetnow/proto2rapidjson

#define RAPIDJSON_HAS_STDSTRING 1

#include <string.h>

#include <vector>
#include <string>

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/prettywriter.h"

namespace {self.package} {{
{''.join(m.to_struct() for m in self.messages.values())}
}}  // namespace {self.package}
#endif
'''
