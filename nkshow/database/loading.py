import itertools
from numbers import Number
import numpy as np

import orjson

# %%


def _all_equal(x):
    g = itertools.groupby(x)
    return next(g, True) and not next(g, False)


def _is_leaf(x):
    if isinstance(x, list) and len(x) > 0:
        if isinstance(x[0], Number):
            # check all same type and they are numbers
            return _all_equal(type(xi) for xi in x)
        elif isinstance(x[0], type(None)):
            return _all_equal(type(xi) for xi in x)
    return False


def transform(x):
    if _is_leaf(x):
        if x[0] == None:
            return np.full(len(x), np.nan)
        else:
            return np.array(x)
    elif isinstance(x, (list, tuple)):
        return {f"{i}": transform(xi) for i, xi in enumerate(x)}
    elif isinstance(x, dict):
        res = {k: transform(v) for k, v in x.items()}
        if len(res) == 2 and set(x.keys()) == set(("real", "imag")):
            return res["real"] + 1j * res["imag"]
        else:
            return res
    else:
        raise ValueError(f"Unknown type: {type(x)}")


def _is_history(x):
    if hasattr(x, "keys"):
        ks = x.keys()
        if all(k in ks for k in ["iters"]):
            return True
    return False


from netket.utils import History


def collect_history(x):
    if _is_history(x):
        iters = x.pop("iters")
        return History(x, iters=iters)
    if isinstance(x, dict):
        tree = {}
        for k, v in x.items():
            tree[k] = collect_history(v)
        return tree
    else:
        return x


def loadfile(path):
    with open(path, "rb") as f:
        data = orjson.loads(f.read())

    data = transform(data)
    data = collect_history(data)
    return data
