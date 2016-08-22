## jsonstream: a coding challenge

Luminoso is looking to hire developers who can handle whatever engineering challenges come our way. This task involves a problem we've actually had to deal with in the real world: parsing JSON data that's arriving over an ugly protocol. (We've solved it by now. We want to see you do the same.)


### Ugly JSON streams

We define an *ugly JSON stream* as a potentially infinite stream of JSON objects, sent over an HTTP connection. The JSON objects, which correspond to dictionaries in Python, appear with *no delimiter* between them. You'll need to determine from the structure of JSON where one object ends and another begins.

Except for the strange stream format, this JSON data complies with the json.org standard. Each object is generated using Python's built-in `json` module, though sometimes using non-default settings. The stream contains some literal Unicode characters, so it is encoded using UTF-8.

In order to provide an infinite stream, the connection uses HTTP/1.1's [chunked transfer encoding](http://en.wikipedia.org/wiki/Chunked_transfer_encoding). However, the boundaries between these chunks are unhelpful for decoding the protocol. The chunks contain a random number of bytes from 1 to 1024. They will usually end in the middle of a JSON object, and possibly even in the middle of a UTF-8 character.

This is an example of an ugly JSON stream with three objects:

    {"one": "this is the first object"}{"two": "this is the second object", "empty_list": []}{"three": 3}


### Pretty JSON streams

What we'd really like to see is a *pretty JSON stream*. A pretty JSON stream is almost the same as an ugly JSON stream, with these differences:

- The objects are separated by line breaks.
- Line breaks may not appear within an object; they may only be used to separate objects.

Pretty JSON streams are much easier to decode than ugly ones.

This is an example of a pretty JSON stream with three objects:

    {"one": "this is the first object"}
    {"two": "this is the second object", "empty_list": []}
    {"three": 3}


### The server

Running `ugly_json_server.py` will start an HTTP server on port 8001, serving an infinite stream of random data via the "ugly JSON stream" protocol. Once it's running, you can look at its output using a command-line HTTP tool such as `curl`:

    curl -s localhost:8001

`ugly_json_server.py` will give you fairly messy data, ensuring that your code can handle all the cases that can come up in JSON.



### Command-line options

Your client should be able to handle the infinite stream, but as part of testing, you may want to end the stream after a certain number of objects. You can do this using the `--limit` command-line option:

    python ugly_json_server.py --limit 100

To get repeatable output from the server, you can also set the random seed:

    python ugly_json_server.py --limit 100 --seed 1

For a summary of the command-line options, run `python ugly_json_server.py --help`.


### Your task

Your task is:

- Write a client that connects to this server, and prints (on standard output) the same data as a pretty JSON stream.
- Write test cases that confirm that your client works correctly. (We suggest using a framework such as Python's `unittest`, `py.test`, or `nose` for this.)

Keep these goals in mind:

- Your code should accomplish the task correctly.
- Your test cases should pass, demonstrating that your code is correct, and they should be specific enough that they would most likely fail if your code were not correct.
- Your code should reflect good programming practices, and not do things that are unsafe or needlessly inefficient.
- Your code should be understandable and pleasant to read.

You can use standard libraries to whatever extent is appropriate.


### Resources

We'd rather you be able to focus on the core problem here, rather than getting stuck on lower-level details. In that spirit, we offer these two hints:

* Python's built in [`JSONDecoder.raw_decode()`](https://docs.python.org/3/library/json.html#json.JSONDecoder.raw_decode) method can be used to find a single JSON document at the beginning of a longer string.
* The [Requests](http://www.python-requests.org/) library (available through PyPI) [makes it easy](http://docs.python-requests.org/en/master/user/quickstart/#raw-response-content) to iterate over a streaming HTTP response. 


### Submitting your code

We are a Python shop and we're best at understanding code in Python, but if you're more comfortable with a similar programming environment such as Ruby or node.js, you may use that for your code sample.

When your code is ready, package it up and send it to `hiring@luminoso.com`, along with any necessary instructions on how to run the client and the test cases. Please send it only to us, and don't make your code publicly available.

We review code samples anonymously, so please DO NOT PUT YOUR NAME in any of your files or filenames.
