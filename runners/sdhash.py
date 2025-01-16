from lib.core import Runner
import fuzzylib

class SDHash(Runner) :

    def run(self, pairs):
        return fuzzylib.sdhash.batch_hash(iter((
            (str(ref), str(alt)) for ref, alt in pairs)))
