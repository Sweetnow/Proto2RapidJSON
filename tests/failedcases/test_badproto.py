#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from typing import Type
import pytest
from proto2rapidjson import entry
from proto2rapidjson.parser import TokenError


def pipeline(name: str, error: Type[Exception]):
    # Step 1: proto -> h
    parent = os.path.dirname(__file__)
    proto_path = os.path.join(parent, f'proto/{name}.proto')
    header_path = os.path.join(parent, '../cpp/proto.h')
    with pytest.raises(error):
        entry(proto_path, header_path, True)

    if os.path.exists(header_path):
        os.remove(header_path)


def test_nopackage():
    pipeline('nopackage', TokenError)


def test_nomessage():
    pipeline('nomessage', TokenError)


def test_invalid_id():
    pipeline('invalid_id', ValueError)


def test_broken_message():
    pipeline('broken_message', TokenError)


def test_use_before_define():
    pipeline('use_before_define', TokenError)


def test_noid():
    pipeline('noid', TokenError)


def test_nonumber():
    pipeline('nonumber', TokenError)


def test_message_same_id():
    pipeline('message_same_id', Exception)


def test_element_same_id():
    pipeline('element_same_id', Exception)
