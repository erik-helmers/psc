from pathlib import Path
import pandas as pd
from typing import NamedTuple


class Runner:

    def id(self): return self.__class__.__name__.lower()

    def run(self, pairs):
        raise NotImplementedError()

class HashDistRunner(Runner):
    """ Use this runner when you simply need to hash  the
        files then compare your hashes
    """
    def __init__(self):
        self.artifacts = dict()

    def run(self, pairs):
        for ref, alt in pairs:
            href = self._get_or_compute(ref, self.hash)
            halt = self._get_or_compute(alt, self.hash)
            yield (ref, alt, self.distance(href, halt))

    def hash(self, path):
        """Given a path name, return its hash"""
        raise NotImplementedError("Override me!")


    def distance(self, href, halt):
        """Given two hashes, return their distances"""
        raise NotImplementedError("Override me!")

    def _get_or_compute(self, key, compute):
        if key not in self.artifacts: self.artifacts[key] = compute(key)
        return self.artifacts[key]

class Benchmark:

    def __init__(self, id, pairs, metadata):
        self._id = id
        self._pairs = pairs
        self._metadata = metadata

    def id(self) -> str:
        return self._id

    def pairs(self):
        return self._pairs

    def metadata(self, path: Path):
        return self._metadata[path]

    """ Create a new Benchmark instance from the specified root path (relative to
        the benchmarks root directy) """
    @staticmethod
    def from_path(root: Path, path: Path):
        files = [
            p.relative_to(root)
            for p in path.iterdir()
            if p.is_file()
        ]
        metadata = {
            path: Benchmark.path_metadata(path)
            for path in files
        }
        pairs = [
            (Benchmark.path_reference(path), path)
            for path in files
            if not metadata[path].get('ref')
        ]
        return Benchmark(str(path.relative_to(root/"benchmarks")), pairs, metadata)

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

class Core:

    def __init__(self, data_root: Path):
        from .cache import Cache, session_from_path
        from runners import RUNNERS
        self.root = data_root
        self._benchmarks = [
            Benchmark.from_path(self.root, path)
            for path in (self.root / "benchmarks").iterdir()
            if not path.is_file()
        ]

        self._runners = RUNNERS
        self._cache = Cache(session_from_path(self.root / "cache.sqlite"))

    def benchmarks(self):
        return list(map(Benchmark.id, self._benchmarks))

    def runners(self):
        return list(map(Runner.id, self._runners))

    def __runner_by_id(self, runner):
        return next(filter(lambda r: r.id() == runner, self._runners))
    def __benchmark_by_id(self, benchmark):
        return next(filter(lambda b: b.id() == benchmark, self._benchmarks))

    """
    All of this library revolves around this method : given some runners
    (ie. some fuzzy-hash implementations), we run a bunch of benchmarks
    and we return the results as a dataframe containing the following :
       - `algo` : the id of the algo that provided this result
       - `bench`: the id of the benchmark that was used
       - `ref`  : the reference file (ie. a path relative to the bench root)
       - `alt`  : the alternative file (ie. a path relative to the bench root)
       - `mods` : the metadata about the relation between `ref` and `alt`
       - `dist` : the distance (a float) as computed by the runner
    """
    def run(self, runners, benchs) -> pd.DataFrame :
        def rel(path): return path.relative_to(self.root)
        def abs(path): return self.root / path
        rows = []
        for runner in runners:
            for bench in benchs:
                runner = self.__runner_by_id(runner)
                bench = self.__benchmark_by_id(bench)
                runner = Core.CachedRunner(self.root, self._cache, runner)
                results = runner.run(bench.pairs())
                rows.extend([
                    (runner.id(), bench.id(),
                     rel(ref), rel(alt),bench.metadata(rel(alt)), dist)
                    for ref, alt, dist in results
                ])
        df = pd.DataFrame(rows, columns=['algo', 'bench', 'ref', 'alt', 'mods', 'dist'])
        return df


    class CachedRunner(Runner):
        def __init__(self, root, cache, runner):
            self.root = root
            self.cache = cache
            self.runner = runner

        def id(self):
            return self.runner.id()

        def run(self, pairs):
            # There is a bit of a relative/absolute path hell, here's an explanation :
            #   * Different components requires different path types
            #   * Everything that is not touching the file system per se needs to
            #     have relative paths : this includes the cache, benchs, etc
            #   * However, the runners use absolute paths and
            def rel(*paths): return tuple([path.relative_to(self.root) for path in paths])
            def abs(*paths): return tuple([self.root / path for path in paths])
            results, remaining = self.cache.get_results(self.runner.id(), pairs)
            results_to_save = []
            for ref, alt, dist in self.runner.run([abs(*pair) for pair in remaining]):
                ref, alt = rel(Path(ref), Path(alt))
                results.append((ref, alt, dist))
                results_to_save.append((ref, alt, dist))
            self.cache.save_results(self.runner.id(), results_to_save)
            return [(*abs(ref,alt), dist) for ref,alt,dist in results ]
