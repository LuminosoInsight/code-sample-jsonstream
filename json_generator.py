#/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function
"""
This file runs an HTTP server on port 8001. When you connect to it, you'll
get an infinite stream of random JSON objects, with no delimiter between them.

The stream is in HTTP 1.1 chunked transfer encoding, which any reasonable
HTTP client should be able to handle. The boundaries between chunks will be
extremely unhelpful, however. The chunks end after a random number of bytes
from 1 to 1024. They will usually end in the middle of a JSON object, and
possibly even in the middle of a UTF-8 character.
"""

import random
import json
import sys

if sys.version_info.major >= 3:
    unichr = chr
    from http.server import HTTPServer, BaseHTTPRequestHandler
else:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


def make_random_characters():
    def random_char():
        if random.randint(0, 9):
            return unichr(random.randrange(0, 0xd800))
        else:
            return unichr(random.randrange(0xe000, 0x110000))
    return ''.join(random_char() for i in range(random.randint(1, 4)))


def make_random_scalar():
    if random.random() < 0.2:
        return make_random_characters()
    else:
        return random.choice([
            'yes', 'no', 'maybe', ':)', '', float('nan'), float('inf'),
            float('-inf'), '🁵🂊🂇',
            '[{"This looks like JSON": "but it\'s actually a string"}]',
            "'", '"', "hello, world", '{', '}', '[',
            ']', "back\\slash", "\\\"\\\\", "\x00", "漢字", -1, 0, 1, 2, 3, 5,
            8, 0.0, 10000, 3.14159, 6.02e23, 1e-30, True, False, None
        ])


def make_random_string():
    if random.random() < 0.2:
        return make_random_characters()
    else:
        return random.choice([
            '', 'a', 'um', 'foo', 'quack', ',', ':', '"',
        ])


def make_random_dict(depth=0):
    maxlength = max(10 - depth, 1)
    length = random.randint(0, maxlength)
    return {make_random_string(): make_random_value(depth + i)
            for i in range(length)}


def make_random_list(depth=0):
    maxlength = max(10 - depth, 1)
    length = random.randint(0, maxlength)
    return [make_random_value(depth + i) for i in range(length)]


def make_random_value(depth=0):
    choice = random.randint(0, 4)
    if choice == 1:
        return make_random_list(depth)
    elif choice == 2:
        return make_random_dict(depth)
    else:
        return make_random_scalar()


def make_random_json():
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


def generate_chunks():
    """
    Generate an infinite, chunked stream of bytes. These bytes will form valid
    JSON objects, but the boundaries of the chunks are not in any way aligned
    with the boundaries of the JSON objects.

    Each chunk will contain 1 to 1024 bytes, inclusive.
    """
    random.seed(0)
    buf = b''
    while True:
        chunk_size = make_random_chunk_size()
        while len(buf) < chunk_size:
            buf += make_random_json().encode('utf-8')
        to_send = buf[:chunk_size]
        buf = buf[chunk_size:]
        yield to_send


class ChunkingRequestHandler(BaseHTTPRequestHandler):
    '''
    A simple HTTP server that serves HTTP 1.1 chunked encoding.

    Based loosely on a public-domain Github Gist by Josiah Carlson:
    https://gist.github.com/josiahcarlson/3250376
    '''
    ALWAYS_SEND_SOME = False
    ALLOW_GZIP = False
    def do_GET(self):
        self.protocol_version = b'HTTP/1.1'
        # send some headers
        self.send_response(200)
        self.send_header(b'Transfer-Encoding', b'chunked')
        self.send_header(b'Content-type', b'application/x-ugly-json-stream')

        self.end_headers()

        def write_chunk():
            hex_length = '%X' % len(chunk)
            tosend = hex_length.encode('ascii') + b'\r\n' + chunk + b'\r\n'
            self.wfile.write(tosend)

        # get some chunks
        for chunk in chunk_generator():
            if not chunk:
                continue
            write_chunk()

        # Hypothetically, if the generator ever ended, we should end the stream
        # with this data. We'll never actually get here.
        self.wfile.write(b'0\r\n\r\n')


def chunk_generator():
    # generate some chunks
    for chunk in generate_chunks():
        yield chunk


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8001), ChunkingRequestHandler)
    server.serve_forever()

