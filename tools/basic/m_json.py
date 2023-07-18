import json
import collections


def read_json(path, mode="r"):
    with open(path, mode, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=collections.OrderedDict)
