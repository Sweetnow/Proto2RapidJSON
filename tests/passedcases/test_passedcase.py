#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from proto2rapidjson import entry


def pipeline(name: str):
    # Step 1: proto -> h
    parent = os.path.dirname(__file__)
    proto_path = os.path.join(parent, f'proto/{name}.proto')
    header_path = os.path.join(parent, '../cpp/proto.h')
    entry(proto_path, header_path, True)

    # Step 2: h -> out
    cpp_path = os.path.join(parent, '../cpp/')
    subprocess.call(['make', 'clean'], cwd=cpp_path)
    assert(subprocess.call(['make'], cwd=cpp_path) == 0)

    # Step 3: parse json
    exe_path = os.path.join(parent, '../cpp/main.out')
    json_path = os.path.join(parent, f'json/{name}.json')
    assert(subprocess.call([exe_path, json_path]) == 0)

    # clean
    subprocess.call(['make', 'clean'], cwd=cpp_path)
    os.remove(header_path)

def test_type():
    pipeline('type')

def test_nest():
    pipeline('nest')

def test_array():
    pipeline('array')

def test_simple():
    pipeline('simple')

def test_more():
    pipeline('more')

def test_comment():
    pipeline('comment')
