import  sys,  progress.bar
from pathlib import Path

from actions import *


def main():
    out_dir = Path(sys.argv[1])
    paths = list(map(Path, sys.argv[2:]))

    bar = progress.bar.IncrementalBar('Generating', max=len(paths)*(len(paths)-1)/2)
    for i,ref in enumerate(paths):
        for _,alt in enumerate(paths[i+1:]):
            ref_filename = f"{ref.stem}.ref{ref.suffix}"
            alt_filename = f"{ref.stem}.alt-{alt.stem}{ref.suffix}"
            shutil.copy(ref, out_dir / ref_filename)
            shutil.copy(alt, out_dir / alt_filename)
            bar.next()

if __name__ == '__main__':
    main()
