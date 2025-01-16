from lib.core import Runner
import fuzzylib

class Nilsimsa(Runner) :

    def run(self, pairs):
        return fuzzylib.nilsimsa.batch_hash(iter((
            (str(ref), str(alt)) for ref, alt in pairs)))
