from pathlib import Path
import pandas as pd
from dataclasses import dataclass, field
from typing import Any, Callable, overload
import os
import json
from dataclasses import dataclass, field
from typing import Any, Callable, overload
import os


class Store(list):

    def by_id(self, id):
        """ Return the first element with the given id. """
        if not hasattr(self, '__ids'): self.__ids = {}


        if obj := self.__ids.get(id, None): return obj

        # > Theree are 2 hard problems in computer science:
        # >   - Naming things
        # >   - Cache invalidation
        # >   - Off by one errors
        # Here our cache will be wrong if elements are removed from the list
        # but we don't care about that for now.
        self.__ids = { obj.id: obj for obj in self }
        if obj := self.__ids.get(id, None): return obj
        raise ValueError(f"Item with id '{id}' not found")

    def by_ids(self, ids):
        """ Return the first element with the given id. """
        return [self.by_id(id) for id in ids]





@dataclass
class Mod:
    """ This represents a modification that was applied to a a reference (ref) file
        to produce an alternative (alt) file.
    """
    id: str
    name: str
    description: str


@dataclass
class Entry:
    """ This represents a pair of files that should be compared.
        The reference file (ref) is an "original" file, and the alternative file (alt)
        was produced by applying a series of modifications (mods) to the reference file.
    """
    ref: str
    alt: str
    mods: dict[str, Any] = field(default_factory=dict) # mod id, value pairs



@dataclass
class Benchmark:
    id: str
    name: str
    content_type: str
    description: str
    cover: str | None # Path to cover image if not None
    entries: list[Entry] = field(default_factory=list)


@dataclass
class Runner:
    id: str
    name: str
    description: str
    run: Callable[[list[tuple[str,str]]], list[float]]

@dataclass
class Result:
    entry: Entry
    runner: Runner
    distance: float



def find_all_benchmarks(root) -> list[Benchmark]:
    out = []
    for directory in root.iterdir():
        if not directory.is_dir(): continue
        out.extend(read_benchmarks(root, directory))

    return out


def read_benchmarks(root, directory) -> list[Benchmark]:

    description = directory / "description.json"
    if not description.exists():
        print("Warning: No description file found in directory... skipping", directory)
        return []

    out = []

    with open(description) as f:
        data = json.load(f)

    for bench in data:
        bench["entries"] = [read_entry(e, root, directory) for e in bench["entries"]]
        out.append(Benchmark(**bench))

    return out

def read_entry(data, root, directory) -> Entry:

    ref = directory / data["ref"]
    alt = directory / data["alt"]

    if not ref.exists(): raise FileNotFoundError(f"Reference file '{ref}' not found")
    if not alt.exists(): raise FileNotFoundError(f"Alternative file '{alt}' not found")

    ref = ref.relative_to(root)
    alt = alt.relative_to(root)

    return Entry(ref=ref, alt=alt, mods = data["mods"])


def compute_results(root: Path, runner, entries, cache = None):
    if not entries: return []

    results = [Result(entry, runner, None ) for entry in entries] # type: ignore

    if cache is not None: cache.populate_results(results)

    distances = runner.run([(root/e.ref, root/e.alt) for e in entries])
    for idx, dist in enumerate(distances):
        results[idx].distance = dist

    return results


from .cache import Cache


class Core:
    """ This class glues together the various components of the benchmark system.
        It is responsible for loading benchmarks, running them, and storing results.
    """
    cache: 'Cache'

    def __init__(self, data: Path | None = None):
        self.data_path = data or Path(os.getenv("DATA_PATH", Path(__file__).parent / "../data"  ))
        self.cache_path = self.data_path / "results.sqlite"
        self.bench_path = self.data_path / "benchmarks"

        self.benchmarks = Store(find_all_benchmarks(self.bench_path))

        from runners import runners
        self.runners = Store(runners)

        self.cache = Cache(self.cache_path)

        print(f"Core initialized at {self.data_path} with {len(self.benchmarks)} benchmarks and {len(self.runners)} runners")

    @overload
    def run(self, runner: Runner, entries: Benchmark | list[Entry]) -> list[Result]: ...
    @overload
    def run(self, runner: Runner, entries: Entry) -> Result: ...

    def run(self, runner: Runner, entries: Benchmark | Entry | list[Entry]) -> list[Result] | Result :
        """ Run a benchmark and return the results.
            If entries is a Benchmark, run all entries in the benchmark.
            If entries is an Entry, run the entry.
            If entries is a list of Entries, run all entries in the list.
        """
        if isinstance(entries, Benchmark):
            _entries = entries.entries
        elif isinstance(entries, Entry):
            _entries = [entries]
        else : _entries = entries

        out = compute_results(self.bench_path, runner, _entries, self.cache)

        return out[0] if isinstance(entries, Entry) else out


    def build_df(self, benchmarks = [], entries = [], runners = [], ):

        _entries = [(b.id, e) for b in benchmarks for e in b.entries]
        _entries += [("", e) for e in entries]

        exclude_bench = int(len(benchmarks) == 0)

        if runners:
            cols : Any = ["bench", "ref", "alt", "distance", "runner"][exclude_bench:]
            rows = []
            for r in runners:
                res = self.run(r, [e for _, e in _entries])
                rows += [ [b, str(e.ref), str(e.alt), res.distance, r.id][exclude_bench:]
                        for (b, e), res in zip(_entries, res)]

        else:
            cols = ["bench", "ref", "alt"][exclude_bench:]
            rows = [ [b, str(e.ref), str(e.alt)][exclude_bench:]
                      for (b, e) in _entries]

        out = pd.DataFrame(rows, columns=cols)
        return  out
