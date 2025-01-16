import os, sys, random, progress.bar
from pathlib import Path
import re

from actions import *


class TextAction(Action):
    def __init__(self, aux, *factors):
        super().__init__(*factors)
        if not isinstance(aux, Path):
            raise ValueError("`aux` must be a Path object")
        self.aux = open(aux, 'r', encoding='utf-8').read()

    def apply(self, inp: Path, out: Path):

        with open(inp, 'r', encoding='utf-8') as f:
            text = f.read()
        with open(out, 'w', encoding='utf-8') as f:
            f.write(self.transform(text))

    def transform(self, text: str) -> str:
        raise NotImplementedError("Override me!")


class Add(TextAction):
    nargs = 2
    def name(self):
        no_blocks, block_size = self.factors
        return f"add_bn-{no_blocks}.add_bs-{block_size}"
    def transform(self, text: str):
        no_blocks, block_size = self.factors

        locations = set() # Locations where to add text
        while len(locations) < no_blocks: locations.add(random.randint(0,len(text)-1))

        output = list(text)
        for i,loc in enumerate(locations):
            start = random.randint(0,len(self.aux)-block_size) # We take the sequence doc2[start:start+size]
            insert = loc+i*block_size
            output[insert:insert] = self.aux[start:start+block_size]

        return "".join(output)


class Swap(TextAction):
    nargs = 2
    def name(self):
        no_blocks, block_size = self.factors
        return f"swap_bn-{no_blocks}.swap_bs-{block_size}"

    def transform(self, text: str):
        no_blocks, block_size = self.factors

        locations = set() # Locations where to add text
        while len(locations) < no_blocks: locations.add(random.randint(0,len(text)-1))

        output = list(text)
        for i,loc in enumerate(locations):
            start = random.randint(0,len(self.aux)-block_size) # We take the sequence doc2[start:start+size]
            insert = loc+i*block_size
            output[insert:insert+block_size] = self.aux[start:start+block_size]

        return "".join(output)

def main():
    out_dir = Path(sys.argv[1])
    # This is used when "deluting" other files
    ref = Path(sys.argv[2])
    paths = list(map(Path, sys.argv[3:]))

    actions = [Ref(), Swap(ref, 8, 1000), Swap(ref, 1000, 8), Add(ref, 8, 1000), Add(ref, 1000, 8)]

    bar = progress.bar.IncrementalBar('Generating', max=len(actions) * len(paths))
    for path in paths:
        for action in actions:
            action.run(path, out_dir)
            bar.next()

if __name__ == '__main__':
    main()
