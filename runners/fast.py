from core.core import Runner
from pathlib import Path
import fuzzylib
from typing import Any

# Dirty hack
fuzzylib: Any = fuzzylib


def fuzzylib_runner(algo) -> Any:

    def run(pairs):
        idx = { (str(ref),str(alt)): i for i, (ref, alt) in enumerate(pairs) }
        res = algo.batch_hash(iter((
            (str(ref), str(alt)) for ref, alt in pairs)))

        out = [None] * len(pairs)
        for ref, alt, dist in res:
            out[idx[(ref, alt)]] = dist

        return out

    return run



runners = [
    Runner("nilsimsa-rs", "Nilsimsa", "Custom implementation of nilsisma",  fuzzylib_runner(fuzzylib.nilsimsa)),
    Runner("tlsh-rs", "TLSH", "Custom implementation of tlsh", fuzzylib_runner(fuzzylib.tlsh)),
    # Runner("ssdeep-rs", "ssdeep", "Custom implementation of ssdeep", fuzzylib_runner(fuzzylib.ssdeep)),
    # Runner("lzjd-rs", "LZJD", "LZJD (rust)", fuzzylib_runner(fuzzylib.lzjd)),
]
