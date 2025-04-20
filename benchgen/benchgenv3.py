
from core.core import Benchmark, Entry

from pathlib import Path
from typing import Any
from abc import ABC, abstractmethod
import random
import string
import shutil
import json

class Generator:

    benchmark: Benchmark

    """ The following properties are actually delegated to the benchmark object."""
    id: str
    name: str
    content_type: str
    description: str
    cover: str
    entries: list[Entry]

    def __init__(self, out_dir: Path):
        self.benchmark = Benchmark(id, None, None, None, None) #type: ignore
        self.out_dir = out_dir

    def try_restore(self, id: str, path: Path):
        """" Essaie de restaurer un benchmark à partir du répertoire out_dir.
             La restauration ne prend en compte que les champs de description
        """
        description = path / "description.json"

        with open(description, "r") as f:
            for obj in json.load(f):
                if obj["id"] == id:
                    self.benchmark = Benchmark(**json.load(f))
                    self.benchmark.entries = []


    def apply_action(self, in_dir: Path, action: 'Action'):
        self.out_dir.mkdir(parents=True, exist_ok=True)

        for in_file in in_dir.iterdir():

            if not in_file.is_file(): continue
            if in_file.name.startswith("."): continue

            # Copy file to out_dir if needeed
            if not (self.out_dir / in_file.name).exists():
                shutil.copy(in_file, self.out_dir / in_file.name)
            in_file = self.out_dir / in_file.name

            id = sum(1 for e in self.entries if e.ref == in_file)
            out_name = f"{in_file.stem}.{id}.{in_file.suffix[1:]}"
            out_file = self.out_dir / out_name

            if out_file.exists(): print(f"Warning: {out_file} already exists, overwritting.")

            action.transform(in_file, out_file)

            entry = Entry(in_file, out_file, expect_similar=False, mods=action.mods())
            self.entries.append(entry)

    def add_file(self, path: Path):
        shutil.copy(path, self.out_dir / path.name)

    def finalize(self):
        desc = self.out_dir / "description.json"

        if desc.exists():
            with open(desc, "r") as f:
                benchs = list(filter(lambda obj: obj["id"] != self.id, json.load(f)))
        else: benchs = []

        bench = self.benchmark.asdict(self.out_dir)

        with open(desc, 'w') as f:
            json.dump(benchs + [bench], f, indent=4)

    def __enter__(self): return self

    def __exit__(self, exc_type, _exc_val, _exc_tb):
        if exc_type is not None: return False
        self.finalize()



for prop in ["id", "name", "content_type", "description", "cover", "entries"]:
    setattr(Generator, prop, property(
        lambda self, prop=prop: getattr(self.benchmark, prop),
        lambda self, value, prop=prop: setattr(self.benchmark, prop, value)
    ))


class Action(ABC):

    def name(self)-> str:
        return f""

    @abstractmethod
    def mods(self) -> dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def transform(self, in_file: Path, out_file: Path):
        raise NotImplementedError()



class ReplaceImage(Action):
    """ Action de remplacer des blocs de pixels dans une image BMP. La taille des blocs en pourcentage de la taille de l'image est spécifiée
    par "rel_size" qui est un flottant compris entre 0 et 1 : 0.5 signifie qu'on remplace la moitié de l'image.
    Le nombre d'ajouts est spécifié par "nb_add".
    Les blocs de pixels sont tirés aléatoirement si "source" est None (par défaut) ou tirés d'une image BMP dont le chemin d'accès

    """

    def __init__(self, nb_add: int, rel_size: float, source: Path | None = None ):
        if source and not source.exists():
            raise ValueError(f"Le fichier source n'existe pas : {source.absolute()}")
        if source and not source.suffix.lower() == ".bmp":
            raise ValueError("Le fichier source doit être au format .bmp", source.absolute())

        self.nb_add = nb_add
        self.rel_size = rel_size
        self.source = source



    def mods(self):
        return {"nb_add" : self.nb_add, "rel_size" : self.rel_size, "source" : str(self.source) }

    def transform(self, in_file: Path, out_file: Path):
        if not in_file.suffix.lower() == ".bmp":
            raise ValueError("Le fichier doit être au format .bmp", in_file.absolute())

        from PIL import Image

        img = Image.open(in_file)
        img = img.convert("RGB")
        pixels = list(img.getdata())
        block_size = int(self.rel_size *len(pixels) )
        output = pixels[:]

        if self.source is not None:
            src = Image.open(self.source)
            src = src.convert("RGB")
            pixels_src = list(src.getdata())

        for _ in range(self.nb_add):
            start_block = random.randint(0, len(pixels) - block_size)
            if self.source is not None:
                start_block_source = random.randint(0,len(pixels_src) - block_size)
                block = pixels_src[start_block_source:start_block_source + block_size]
            else:
                block = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(block_size)]

            output[start_block:start_block+block_size] = block

        img_transformed = Image.new("RGB", img.size)
        img_transformed.putdata(output)
        img_transformed.save(out_file, "BMP")


class AddText(Action):
    """Rallonge un texte en ajoutant nb_add blocs de taille rel_size*len(texte) à un texte.
    L'ajout est par défaut composé de caractères ASCII aléatoires mais peut être tiré d'un fichier texte
    dont le chemin d'accès est spécifié par la variable "source".
    """
    def __init__(self, nb_add: int, rel_size: float, source: Path | None = None):
        self.nb_add = nb_add
        self.rel_size = rel_size
        self.source = source


    def mods(self):
        return {"nb_add" : self.nb_add, "rel_size" : self.rel_size, "source" : self.source}

    def transform(self, in_file: Path, out_file: Path):
        with in_file.open("r") as in_:
            content = in_.read()

        block_size = int(self.rel_size * len(content))


        if self.source is not None:
            with self.source.open("r") as source_file:
                src = source_file.read()

        for _ in range(self.nb_add):
            start = random.randint(0, len(content))
            if self.source is None:
                random_chars = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=block_size))
                content = content[:start] + random_chars + content[start:]
            else:
                start_source = random.randint(0, len(src))
                content = content[:start] + src[start_source:start_source + block_size] + content[start:]

        with open(out_file, "w") as out:
            out.write(content)


class SwapText(Action):
    """
    Action de swap: échange des parties d'un texte .txt. Réalise nb_swaps échanges aléatoires
    avec des blocs de taille rel_size*len(image): rel_size est un flottant entre 0 et 1 qui
    représente la taille des blocs à échanger en pourcentage de la longueur du fichier. Ce paramètre
    doit être inférieur à 1/3.
    """
    def __init__(self, nb_swaps: int, rel_size: float):
        self.nb_swaps = nb_swaps
        self.rel_size = rel_size

    def mods(self):
        return {"nb_swaps" : self.nb_swaps, "rel_size" : self.rel_size}

    def transform(self, in_file: Path, out_file: Path):
        with in_file.open("r") as in_:
            content = list(in_.read())

        block_size = int(self.rel_size * len(content))

        for _ in range(self.nb_swaps):
            start1 = random.randint(0, len(content) - block_size)
            start2 = random.randint(0, len(content) - 2*block_size)

            if start2 >= start1: start2 += block_size

            end1 = start1 + block_size
            end2 = start2 + block_size

            content[start1:end1], content[start2:end2] = content[start2:end2], content[start1:end1]

        with open(out_file, "w") as out:
            out.write("".join(content))
