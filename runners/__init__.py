from .fast import Tlsh, Nilsimsa, SSDeep
from .sdhash import Sdhash

RUNNERS = [
    Tlsh(),
    Nilsimsa(),
    SSDeep(),
    Sdhash(),
]
