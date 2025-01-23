from pathlib import Path
from functools import reduce
from collections import defaultdict
import numpy as np

def pretty(df):
    df['ref'] = df['ref'].apply(lambda x: Path(x).name)
    df['alt'] = df['alt'].apply(lambda x: Path(x).name)

    df = with_mods(df)
    df = suffix(df)
    df = wide(df)
    return df

def with_mods(df):
    df['mods'] = df['meta'].apply(lambda x: {
        k: x[k]  for k in x.keys() - {"ref", "alt", "dist"}})
    return df

def wide(df):
    base = reduce(lambda x, y: x|y, df['mods'], {})
    for param in base.keys():
        default = {int: 0, bool: False, str: ""}.get(type(base[param]))
        df[param] = df['mods'].apply(lambda x: x.get(param, default))
    return df

def long(df):
    base = reduce(lambda x, y: x|y, df['mods'], {})
    idx = df.columns.difference(base.keys())[::-1]
    df = df.melt(id_vars=idx, var_name="mod", value_name="modval")
    df = df.loc[df['modval']!=0, :]
    df['mod'] = df['mod'].astype('category')
    return df

def suffix(df):
    df['suffix'] = df['ref'].apply(lambda x: x.rsplit('.')[-1])
    return df



""" Compute the histogram of n-grams in the binary blob """
def ngrams(n, bytes_):
    out = np.zeros([256]*n, dtype=np.uint32)
    for i in range(len(bytes_)-n+1):
        out[tuple(bytes_[i:i+n])] += 1
    return out

