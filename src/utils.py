import os


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def merge_dict(dst, src):
    for k, v in src.items():
        if k in dst and isinstance(dst[k], dict) and isinstance(v, dict):
            merge_dict(dst[k], v)
        else:
            dst[k] = v
    return dst
