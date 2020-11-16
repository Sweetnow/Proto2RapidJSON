#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from proto2rapidjson import scan, Parser


if __name__ == "__main__":
    input = '''
package first;

// comment
message Sub {
    // comment
    double sub1 = 1;
    int32 sub2; // comment
}

message Main {
    repeated Sub sub;
}
    '''
    parser = Parser(scan(input))
    with open('output.h', 'w') as f:
        f.write(parser.tocpp())

    # print(scan(input))
