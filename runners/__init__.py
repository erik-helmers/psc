from .fast import Tlsh, Nilsimsa, SSDeep, Lzjd
from .sdhash import Sdhash

RUNNERS = [
    Lzjd(),
    Tlsh(),
    Nilsimsa(),
    SSDeep(),
    Sdhash(),
]
