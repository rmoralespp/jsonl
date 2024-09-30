# -*- coding: utf-8 -*-

import collections

import jsonl

extensions = (".jsonl", ".gz", ".bz2", ".xz", ".unknown")

# https://jsonlines.org/examples/
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "Alexa", "wins": [["two pair", "4♠"], ["two pair", "9♠"]]},
    {"name": "May", "wins": []},
    {"name": "Deloise", "wins": [["three of a kind", "5♣"]]},
]

string_data = (
    '{"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]}\n'
    '{"name": "Alexa", "wins": [["two pair", "4♠"], ["two pair", "9♠"]]}\n'
    '{"name": "May", "wins": []}\n'
    '{"name": "Deloise", "wins": [["three of a kind", "5♣"]]}\n'
)


def read_text(filename):
    with jsonl.xopen(filename, mode="rt") as f:
        return f.read()


def write_text(filename, content=""):
    with jsonl.xopen(filename, mode="wt") as f:
        f.write(content)
    return filename


consume = collections.deque(maxlen=0).extend
