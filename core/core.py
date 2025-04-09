from pathlib import Path
import pandas as pd
from typing import NamedTuple


class Runner:

    def id(self): return self.__class__.__name__.lower()

    def run(self, bench):
        raise NotImplementedError()

class PairRunner(Runner):
    """ Use this when you just want the ref/alt paths absolute paths and will
        return them in the form ref/alt/dist
    """
    def run(self, bench):
        pairs = bench.pairs(absolute=True, skip_computed=True)
        res = self.run_on_pairs(pairs)
        for ref,alt,dist in res:
            bench.attrs(ref,alt).dist = dist

    def run_on_pairs(self, pairs):
        raise NotImplementedError("Override me!")


class HashDistRunner(Runner):
    """ Use this when you only need to hash files from paths then compare them
    """
    def __init__(self):
        self._cache = {}

    def run(self, bench):
        pairs = bench.pairs(absolute=True, skip_computed=True)
        for ref,alt in pairs:
            bench.attrs(ref,alt).dist = self.distance(
                self._get_hash(ref),
                self._get_hash(alt),
            )

    def hash(self, path):
        raise NotImplementedError("Override me!")

    def distance(self, href, halt):
        raise NotImplementedError("Override me!")

    def _get_hash(self, path):
        if path not in self._cache:
            self._cache[path] = self.hash(path)
        return self._cache[path]



class Entry:

    def __init__(self, ref, alt):
        self.ref = ref
        self.alt = alt
        self.dist = None


    def __repr__(self):
        return f"({str(self.ref)}, {str(self.alt)}, {str(self.dist)})"

    @staticmethod
    def from_dict(d):
        out = Entry(d['ref'], d['alt'])
        for k,v in d.items():
            if k not in ['ref', 'alt']: setattr(out, k, v)
        return out

class Benchmark:

    def __init__(self, id, root, entries):
        self._id = id
        self._root = root
        self._entries = {(e.ref,e.alt): e for e in entries}

    def id(self) -> str:
        return self._id

    def pairs(self, /, absolute, skip_computed=False):
        """ Get pairs of refpath / altpath of this benchmark """
        if absolute:
            return [(self._root/ref, self._root/alt)
                    for ref, alt in self.pairs(absolute=False, skip_computed=skip_computed)]
        else:
            return [k for (k, entry) in self._entries.items() if entry.dist is None or not skip_computed ]

    def entries(self):
        return self._entries.values()

    def attrs(self, ref: Path, alt: Path):
        if ref.is_relative_to(self._root): ref = ref.relative_to(self._root)
        if alt.is_relative_to(self._root): alt = alt.relative_to(self._root)
        return self._entries[(ref,alt)]

    def copy(self):
        from copy import deepcopy
        return deepcopy(self)

    def __repr__(self) -> str:
        return f"Benchmark({self.id()}, {self.entries()})"

    """ Create a new Benchmark instance from the specified root path (relative to
        the benchmarks root directy) """
    @staticmethod
    def from_path(root: Path, path: Path):
        files = [
            p.relative_to(root)
            for p in path.iterdir()
            if p.is_file() and not p.name.startswith('.')
        ]
        metadata = {
            path: Benchmark.metadata_from_path(path)
            for path in files
        }
        entries = [
            Entry.from_dict({ **metadata[path], 'ref': Benchmark.reference_from_path(path), 'alt': path })
            for path in files
            if not metadata[path].get('ref')
        ]
        return Benchmark(str(path.relative_to(root/"benchmarks")), root, entries)

    @staticmethod
    def metadata_from_path(path):
        modlist = path.stem.split('.')[1:]
        mods : dict[str,object]= {}
        for mod in modlist :
            if not '-' in mod: mods[mod] = True; continue
            key, param = mod.split('-')
            try: mods[key] = int(param)
            except ValueError: mods[key] = param
        return mods

    @staticmethod
    def reference_from_path(path) -> Path :
        return path.parent / (path.stem.split('.')[0] + '.ref' + path.suffix)


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

    def __runner_by_id(self, runner: str) -> Runner:
        try: return next(filter(lambda r: r.id() == runner, self._runners))
        except StopIteration: raise ValueError(f"runner {runner} doesn't exist in {self.runners()}")
    def __benchmark_by_id(self, benchmark: str) -> Benchmark:
        try: return next(filter(lambda b: b.id() == benchmark, self._benchmarks))
        except StopIteration: raise ValueError(f"benchmark {benchmark} doesn't exist in {self.benchmarks()}")

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

    Options:
      - `bypass_cache`: don't use the cache in any way
      - `recompute_cache`: drop the previously cached results: Broken
    """
    def run(self, runners: list[str], benchs: list[str],
            bypass_cache=False, recompute_cache=False) -> pd.DataFrame :
        print(f"Running {runners} with benchs {benchs}")
        rows = []
        for runner_id in runners:
            for bench_id in benchs:
                runner= self.__runner_by_id(runner_id)
                bench = self.__benchmark_by_id(bench_id).copy()

                if not bypass_cache and not recompute_cache:
                    runner = Core.CachedRunner(self.root, self._cache, runner)

                runner.run(bench)
                rows.extend([
                    (runner.id(), bench.id(),
                     e.ref, e.alt, e.dist, vars(e))
                    for e in bench._entries.values()
                ])

                if recompute_cache:
                    results = [(e.ref, e.alt, e.dist) for e in bench.entries()]
                    self._cache.update_results(runner.id(), results)

        df = pd.DataFrame(rows, columns=['algo', 'bench', 'ref', 'alt', 'dist', 'meta'])
        return df


    class CachedRunner(Runner):
        def __init__(self, root, cache, runner):
            self.root = root
            self.cache = cache
            self.runner = runner

        def id(self):
            return self.runner.id()

        def run(self, bench):
            results, _ = self.cache.get_results(self.runner.id(), bench.pairs(absolute=False, skip_computed=True))

            for ref,alt,dist in results:
                bench.attrs(ref,alt).dist = dist
            new_pairs = bench.pairs(absolute = False, skip_computed=True)
            if new_pairs: self.runner.run(bench)
            new_results = [(ref,alt,bench.attrs(ref,alt).dist) for ref,alt in new_pairs]
            self.cache.save_results(self.runner.id(), new_results)
