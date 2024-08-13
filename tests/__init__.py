# -*- coding: utf-8 -*-

import collections


def read(filename):
    with open(filename, encoding="utf-8") as f:
        return f.read()


def write(filename, content=""):
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(content)
    return filename


consume = collections.deque(maxlen=0).extend
