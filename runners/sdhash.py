""" Note: sdhash is expected to be in the directory, good luck compiling it """

from pathlib import Path
import subprocess
import tempfile
from lib.core import HashDistRunner



DIR = Path(__file__).parent
SDHASH_BIN = DIR / "sdhash"
SDHASH_TMP = DIR

class Sdhash(HashDistRunner):

    def hash(self, path):
        return subprocess.check_output([SDHASH_BIN, str(path)], text=True)

    def distance(self, href, halt):
        with tempfile.NamedTemporaryFile(prefix="sdbf_", mode='w+', dir=DIR) as sdbfs:
            sdbfs.writelines([href,halt])
            sdbfs.flush()
            out = subprocess.check_output([SDHASH_BIN,'-c', sdbfs.name], text=True)
        score = float(out.split('|')[-1]) if out else 0
        return 100-score
