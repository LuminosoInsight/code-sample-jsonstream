# jsonstream: a coding challenge

We're looking for someone who can handle whatever engineering challenges come our way. This task involves a problem we've actually had to deal with in the real world: parsing JSON data that's arriving over an ugly protocol. (We've solved it by now. We want to make sure you can do the same.)

## Ugly JSON streams

We define an *ugly JSON stream* as a potentially infinite stream of JSON objects, sent over an HTTP connection. The JSON objects, which correspond to dictionaries in Python, appear with *no delimiter* between them. You'll need to determine from the structure of JSON where one object ends and another begins.

The JSON data complies with the json.org standard. It's all generated using Python's built-in `json` module, though sometimes using non-default settings. It contains some literal Unicode characters, so it is encoded using UTF-8.

In order to provide an infinite stream, the connection uses HTTP/1.1's [chunked transfer encoding](http://en.wikipedia.org/wiki/Chunked_transfer_encoding). However, the boundaries between these chunks will be entirely unhelpful for decoding the protocol. The chunks end after a random number of bytes from 1 to 1024. They will usually end in the middle of a JSON object, and possibly even in the middle of a UTF-8 character.

## Pretty JSON streams

What we'd really like to see is a *pretty JSON stream*. A pretty JSON stream is almost the same as an ugly JSON stream, with these differences:

- The objects are separated by line breaks.
- Line breaks may not appear within an object; they may only be used to separate objects.

Pretty JSON streams are much easier to decode than ugly ones.

## Your task

Running `json_generator.py` will start an HTTP server on port 8001, serving an infinite stream of random JSON data via this protocol.

Your task is to write another server that runs on port 8002, which connects to the unmodified server that's running on port 8001, and outputs a pretty JSON stream with the same content.

