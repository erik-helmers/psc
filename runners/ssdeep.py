from lib.core import Runner
import fuzzylib

class SSDeep(Runner) :

    def run(self, pairs):
        return fuzzylib.ssdeep.batch_hash(iter((
            (str(ref), str(alt)) for ref, alt in pairs)))
