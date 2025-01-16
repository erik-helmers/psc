from lib.core import Runner
import fuzzylib

class Tlsh(Runner) :

    def run(self, pairs):
        return fuzzylib.tlsh.batch_hash(iter((
            (str(ref), str(alt)) for ref, alt in pairs)))
