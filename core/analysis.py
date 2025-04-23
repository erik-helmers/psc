from pathlib import Path
from functools import reduce
import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class ConfusionMatrix:
    raw: np.ndarray

    @property
    def tp(self): return self.raw[0, 0]

    @property
    def fp(self): return self.raw[0, 1]

    @property
    def fn(self): return self.raw[1, 0]

    @property
    def tn(self): return self.raw[1, 1]

    @property
    def tpr(self): return self.tp / (self.tp + self.fn)

    @property
    def fnr(self): return self.fn / (self.tp + self.fn)

    @property
    def tnr(self): return self.tn / (self.fp + self.tn)

    @property
    def fpr(self): return self.fp / (self.fp + self.tn)


    def f_score(self) -> float:
        """Compute the F-score."""
        precision = self.precision()
        recall = self.detection_rate()
        return 2 * (precision * recall) / (precision + recall)

    def precision(self) -> float:
        """Compute the precision."""
        return self.tp / (self.tp + self.fp)

    def error_rate(self) -> float:
        """Compute the error rate."""
        return (self.fp + self.fn) / (self.tp + self.tn + self.fp + self.fn)

    def detection_rate(self) -> float:
        """Compute the detection rate (recall)"""
        if self.tp + self.fn == 0: return 0.0
        return self.tp / (self.tp + self.fn)

    def false_alarm_rate(self) -> float:
        """Compute the false-alarm rate."""
        return self.fp / (self.fp + self.tn)

    def asdict(self):
        """Convert to a dictionary."""
        return {
            'tp': self.tp,
            'fp': self.fp,
            'fn': self.fn,
            'tn': self.tn,
            'tpr': self.tpr,
            'fpr': self.fpr,
            'fnr': self.fnr,
            'tnr': self.tnr,
            'precision': self.precision(),
            'error_rate': self.error_rate(),
            'detection_rate': self.detection_rate(),
            'false_alarm_rate': self.false_alarm_rate(),
            'f_score': self.f_score()
        }


def confusion_matrix(df_pos, df_neg, threshold):
    out = np.zeros((2, 2), dtype=np.int64)

    out[0, 0] = df_pos.loc[df_pos['distance'] <= threshold].size
    out[0, 1] = df_neg.loc[df_neg['distance'] <= threshold].size
    out[1, 0] = df_pos.loc[df_pos['distance'] >  threshold].size
    out[1, 1] = df_neg.loc[df_neg['distance'] >  threshold].size

    return ConfusionMatrix(out)


def confusion_df(df_pos, df_neg, thresholds = None):

    if thresholds is None:
        val_min = min(df_pos['distance'].min(), df_neg['distance'].min())
        val_max = max(df_pos['distance'].max(), df_neg['distance'].max())
        thresholds = np.linspace(val_min, val_max, 100)

    data = []

    for threshold in thresholds:
        cm = confusion_matrix(df_pos, df_neg, threshold)
        dcm = cm.asdict() | { "threshold": threshold }
        data.append(dcm)

    return pd.DataFrame(data)


def pretty(df):
    df['ref'] = df['ref'].apply(lambda x: Path(x).name)
    df['alt'] = df['alt'].apply(lambda x: Path(x).name)

    df = suffix(df)
    df = wide(df)
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

