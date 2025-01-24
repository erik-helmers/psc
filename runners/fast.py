from lib.core import PairRunner
from pathlib import Path
import fuzzylib


""" This is *fast* because it is written in rust btw"""

class FuzzylibRunner(PairRunner):

    algo = None

    def __init__(self, algo = None):
        self.algo = algo or self.algo or self.__class__.__name__.lower()

    def run_on_pairs(self, pairs):
        res = getattr(fuzzylib, self.algo).batch_hash(iter((
            (str(ref), str(alt)) for ref, alt in pairs)))
        return [(Path(ref), Path(alt),dist) for ref, alt, dist in res]

class Nilsimsa(FuzzylibRunner): pass
class Tlsh(FuzzylibRunner): pass
class SSDeep(FuzzylibRunner): pass
class Lzjd(FuzzylibRunner): pass
