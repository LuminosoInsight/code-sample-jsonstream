#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function
"""
This file runs an HTTP server on port 8001. When you connect to it, you'll
get an infinite stream of random JSON objects, with no delimiter between them.

The stream is in HTTP 1.1 chunked transfer encoding, which any reasonable
HTTP client should be able to handle. The boundaries between chunks will be
extremely unhelpful, however.

The server can be configured with command line arguments. For information
on these arguments, run:

    ugly_json_server.py --help

This code will run in Python 2.7 or 3.3, and possibly also in Python 3.2.
"""

import random
import json
import sys
import argparse

# These might be configured by a command line parameter
LIMIT = None
SEED = None

# Handle version differences between Python 2 and 3
if sys.version_info.major >= 3:
    unichr = chr
    from http.server import HTTPServer, BaseHTTPRequestHandler
else:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


if sys.maxunicode < 0x10ffff:
    raise UnicodeError(
        "This version of Python is a 'narrow build', which doesn't support "
        "Unicode characters beyond the first 65536. The server can't run "
        "because it can't generate its full range of test data. We recommend "
        "upgrading to Python 3.3 or later, which always has full support for "
        "Unicode."
    )

def make_random_characters():
    """
    Return a string of random characters from anywhere in Unicode (except
    for surrogates).
    """
    def random_char():
        if random.random() < 0.9:
            return unichr(random.randrange(0, 0xd800))
        else:
            return unichr(random.randrange(0xe000, 0x110000))
    return ''.join(random_char() for i in range(random.randint(1, 4)))


def make_random_scalar():
    """
    Return a random value that doesn't contain other values.
    """
    if random.random() < 0.2:
        return make_random_characters()
    else:
        return random.choice([
            'yes', 'no', 'maybe', ':)', '', '🁵🂊🂇',
            '[{"This looks like JSON": "but it\'s actually a string"}]',
            "'", '"', "hello, world", '{', '}', '[',
            ']', "back\\slash", "\\\"\\\\", "\x00", "漢字", -1, 0, 1, 2, 3, 5,
            8, 0.0, 10000, 6.283185, 6.02e23, 1e-30, True, False, None
        ])


def make_random_string():
    """
    Return a randomly-chosen string.
    """
    if random.random() < 0.2:
        return make_random_characters()
    else:
        return random.choice([
            '', 'a', 'um', 'foo', 'quack', ',', ':', '"', "}{",
        ])


def make_random_dict(depth=0):
    """
    Return a dictionary from random strings to random values. The number of
    values decreases as the recursive 'depth' increases, so that this process
    terminates.
    """
    maxlength = max(10 - depth, 1)
    length = random.randint(0, maxlength)
    return {make_random_string(): make_random_value(depth + i + 1)
            for i in range(length)}


def make_random_list(depth=0):
    """
    Return a list of random values. The number of values decreases as the
    recursive 'depth' increases, so that this process terminates.
    """
    maxlength = max(10 - depth, 1)
    length = random.randint(0, maxlength)
    return [make_random_value(depth + i + 1) for i in range(length)]


def make_random_value(depth=0):
    """
    Return a random list, dictionary, or scalar value.
    """
    choice = random.randint(0, 4)
    if choice == 1:
        return make_random_list(depth)
    elif choice == 2:
        return make_random_dict(depth)
    else:
        return make_random_scalar()


def make_random_json():
    """
    Generate a random dictionary, encode it as JSON with random settings,
    and return that JSON string.
    """
    value = make_random_dict()
    indent = random.choice([None, None, None, None, None, None, 1, 2])
    ensure_ascii = random.choice([True, False])
    separators = random.choice([
        (", ", ": "),
        (", ", ": "),
        (", ", ": "),
        (",", ": "),
        (", ", ":"),
        (",", ":"),
        (" , ", " : "),
        ("  ,", ":  ")
    ])
    return json.dumps(value, indent=indent, ensure_ascii=ensure_ascii,
                      separators=separators)


def make_random_chunk_size():
    choice = random.randint(0, 1)
    if choice == 0:
        return random.choice([1, 2, 4, 1024])
    else:
        return random.randint(1, 1024)


def generate_chunks(limit=None, seed=None):
    """
    Generate a chunked stream of bytes. These bytes will form valid
    JSON objects, but the boundaries of the chunks are not in any way aligned
    with the boundaries of the JSON objects.

    Each chunk will contain 1 to 1024 bytes, inclusive.

    If `limit` is specified, it will stop after `limit` JSON objects. Otherwise,
    the stream will be infinite.
    """
    buf = b''
    count = 0
    if seed is not None:
        random.seed(seed)

    under_limit = True
    while under_limit or len(buf) > 0:
        chunk_size = make_random_chunk_size()
        while len(buf) < chunk_size and under_limit:
            buf += make_random_json().encode('utf-8')
            count += 1
            under_limit = (limit is None or count < limit)
        to_send = buf[:chunk_size]
        buf = buf[chunk_size:]
        yield to_send


class ChunkingRequestHandler(BaseHTTPRequestHandler):
    '''
    A simple HTTP server that serves HTTP 1.1 chunked encoding.

    Based loosely on a public-domain Github Gist by Josiah Carlson:
    https://gist.github.com/josiahcarlson/3250376
    '''
    def do_GET(self):
        self.protocol_version = 'HTTP/1.1'
        # send some headers
        self.send_response(200)
        self.send_header('Transfer-Encoding', 'chunked')
        self.send_header('Content-Type', 'application/x-ugly-json-stream')

        self.end_headers()

        def write_chunk(chunk):
            hex_length = '%X' % len(chunk)
            tosend = hex_length.encode('ascii') + b'\r\n' + chunk + b'\r\n'
            self.wfile.write(tosend)

        # get some chunks
        for chunk in generate_chunks(LIMIT, SEED):
            write_chunk(chunk)

        # If the generator ends, write the final HTTP chunk
        self.wfile.write(b'0\r\n\r\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="set the port number to serve on", type=int, default=8001)
    parser.add_argument("--seed", help="set the random seed", type=int)
    parser.add_argument("--limit", help="send only this many objects per connection", type=int)
    args = parser.parse_args()
    SEED = args.seed
    LIMIT = args.limit
    server = HTTPServer(('127.0.0.1', args.port), ChunkingRequestHandler)
    print("Running server on port {0}.".format(args.port))
    server.serve_forever()
