import json
from functools import reduce


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def merge_dict(dst, src):
    for k, v in src.items():
        if k in dst:
            if isinstance(dst[k], dict) and isinstance(v, dict):
                merge_dict(dst[k], v)
            elif k in dst and isinstance(dst[k], list) and isinstance(v, list):
                v.extend(dst[k])
                dst[k] = v
            else:
                dst[k] = v
        else:
            dst[k] = v
    return dst


def read_json_files(paths: list) -> dict:
    data = [json.loads(read(f)) for f in paths]
    return reduce(lambda a, b: merge_dict(a, b), data)
