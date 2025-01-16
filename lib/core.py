from pathlib import Path
import pandas as pd
from typing import NamedTuple


class Runner:

    def __init__(self, id: str):
        self._id = id

    def id(self): return self._id

    def run(self, pairs):
        raise NotImplementedError()

class Benchmark:

    def __init__(self, id, pairs):
        self._id = id
        self._pairs = pairs

    def id(self) -> str:
        return self._id

    def pairs(self):
        return self._pairs

    """ Create a new Benchmark instance from the specified root path (relative to
        the benchmarks root directy) """
    @staticmethod
    def from_path(path: Path):
        files = list(filter(Path.is_file, path.iterdir())))
        pairs = [
            (Benchmark.path_reference(path), path)
            for path in files
            if not Benchmark.path_metadata(path).get('ref')
        ]
        return Benchmark(str(path), pairs)

    @staticmethod
    def path_metadata(path):
        modlist = path.stem.split('.')[1:]
        mods : dict[str,object]= {}
        for mod in modlist :
            if not '-' in mod: mods[mod] = True; continue
            key, param = mod.split('-')
            try: mods[key] = int(param)
            except ValueError: mods[key] = param
        return mods

    @staticmethod
    def path_reference(path) -> Path :
        return path.parent / (path.stem.split('.')[0] + '.ref' + path.suffix)


Result = NamedTuple("Result", [
    ('runner', str),
    ('bench', str),
    ('ref', Path),
    ('alt', Path),
    ('dist', float),
])

class XXX:

    def __init__(self, data_root: Path):
        self.root = data_root
        self.benchmarks = benchmarks
        self.runners = runners

    def benchmarks(self):
        return list(map(Benchmark.id, self.benchmarks))

    def runners(self):
        return list(map(Runner.id, self.runners))

    """
    All of this library revolves around this method : given some runners
    (ie. some fuzzy-hash implementations), we run a bunch of benchmarks
    and we return the results as a dataframe containing the following :
       - `algo` : the id of the algo that provided this result
       - `bench`: the id of the benchmark that was used
       - `ref` : the reference file (ie. a path relative to the bench root)
       - `alt` : the alternative file (ie. a path relative to the bench root)
       - `dist` : the distance (a float) as computed by the runner
    """
    def run(self, runners, benchs) -> pd.DataFrame :
        pass
