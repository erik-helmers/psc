from .fast import Tlsh, Nilsimsa, SSDeep
from .fbhash_text import Fbhash_text

RUNNERS = [
    Tlsh(),
    Nilsimsa(),
    SSDeep(),
    Fbhash_text()
]
