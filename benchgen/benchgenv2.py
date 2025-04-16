import shutil, re
from pathlib import Path
from PIL import Image
import random
import json
import sys
import string
from abc import ABC, abstractmethod

random.seed(1)  # For reproducibility


class Action(ABC):  # Abstract
    """This module generates file benchmarks from a folder containing different files
    on which we want to test fuzzy-hashing algorithms.
    First, it generates the altered files from the original ones by applying the action.
    Then, it saves the original files and the altered ones in a folder called "benchmark".
    If the original folder is structured as {file1, file2, ...}, it generates a "benchmark.json" file described as:
    [
        {
            "id": "small-add"
            "name": "Small additions",
            "description": "The similar pairs are reference files and their versions modified by
            small text additions with class AddText.",
            "cover": "Path/to/cover/image.png",
            "content_type": "text",
            "entries": [
                {
                    "ref": "fichier1",
                    "alt": "fichier1.add",
                    "expect_similar": true,
                    "mods": {"add" : {"block_size": 4, "nb_block": 1024}}
                }, 
                ... , 
                {
                    "ref": "fichier1";
                    "alt": "fichier2",
                    "expect_similar": false
                    }
            ]
        },
    ]
    id and name identifies the benchmark. The description is a short description of the benchmark.
    The content_type is the type of files in the benchmark (text, image, compiled...).
    Cover is the path to the image used as a cover for the benchmark.
    The entries are the list of pairs of files we want to compare. Each entry contains the reference file and the altered one.
    The expect_similar field is true if we expect the two files to be similar and false otherwise.
    The mods field is a dictionary containing the parameters used to generate the altered file.
    The json file is a list of dictionaries, allowing to construct several benchmarks in the same file.
    """
    def __init__(self, name: str, params: dict, in_dir: Path, out_dir: Path):
        self.name = name
        self.params = params
        self.out_dir = out_dir
        self.in_dir = in_dir
        if not self.in_dir.is_dir():
            raise ValueError(f"{self.in_dir} n'est pas un dossier valide.")
        
        paths = list(self.in_dir.glob("*"))  # Liste de tous les fichiers et dossiers dans self.in_dir
        paths = [f for f in paths if f.is_file()]  # Ne garder que les fichiers
        if not paths:
            raise ValueError(f"Aucun fichier trouvé dans {self.in_dir}.")
        # Vérifier que tous les fichiers ont la même extension
        extensions = {f.suffix for f in paths}
        if len(extensions) > 1:
            raise ValueError(f"Les fichiers du dossier {self.in_dir} n'ont pas la même extension: {extensions}")
        self.paths = paths

    @abstractmethod
    def transform_and_save(self, file: Path, name_alt: str):
        """Prend le fichier situé en "file" et enregistre la version modifiée du fichier dans le dossier 
        self.out_dir sous le nom "file.stem + self.id + file.suffix".
        """
        raise NotImplementedError("Override me!")

    def generate_benchmark(self):
        """Génère le fichier JSON de description du benchmark. Le fichier est enregistré dans le dossier "out_dir" 
        sous le nom "benchmark.json".
        """
        # Create output directory and filing it
        self.out_dir.mkdir(parents=True, exist_ok=True)  # Create the output directory if it doesn't exist
        for path in self.paths:
            shutil.copy(path, self.out_dir / path.name)  # Copy the original files to the output directory
            for i in range(1,17): # Generate several different versions of the file
                random.seed(i)
                self.transform_and_save(path, f'{path.stem}-{i}{path.suffix}') # Transform the original files and save them in the output directory

        # Constructing the json file
        id = self.name.lower()
        name = self.name
        description = ""
        content_type = ""
        cover = ""
        entries = []
        for path in self.paths: # Save pairs of files that are similar
            ref_filename = str(path.name)
            for i in range(1,17):
                alt_filename = f"{path.stem}-{i}{path.suffix}"
                entries.append({"ref": ref_filename, "alt": alt_filename, "expect_similar": True, 
                    "mods": {id : {k: (str(v) if isinstance(v, Path) else v) for k,v in self.params.items()}}})
        
        for i,ref in enumerate(self.paths): # Save pairs of files that are not similar
            for _,alt in enumerate(self.paths[i+1:]):
                entries.append({"ref": str(ref.name), "alt": str(alt.name), "expect_similar": False,
                                "mods": {}})
        
        list_of_benchs = [dict(id=id, name=name, description=description, cover=cover, content_type=content_type, entries=entries)]
        benchmark_dir = self.out_dir / "benchmark.json"
        with benchmark_dir.open("w", encoding="utf-8") as file:
            json.dump(list_of_benchs, file, indent=4, ensure_ascii=False)

class SwapImage(Action):
    """
    Action de swap: échange des parties d'une image .bmp. Réalise nb_swaps échanges aléatoires 
    avec des blocs de taille rel_size*len(image): rel_size est un flottant entre 0 et 1 qui
    représente la taille des blocs à échanger en pourcentage de la longueur du fichier. Ce paramètre 
    doit être inférieur à 1/3.
    """
    def __init__(self, nb_swaps: int, rel_size: float, in_dir: Path, out_dir: Path):
        if rel_size > 1/3:
            raise ValueError(f"La taille des blocs échangés doit être inférieure au tiers du fichier (ici rel_size était {rel_size})")
        params = {"nb_swaps" : nb_swaps, "rel_size" : rel_size}
        super().__init__(name="swap", params=params, in_dir=in_dir, out_dir=out_dir)
    
    def transform_and_save(self, file: Path, name_alt: str):
        if not file.suffix.lower() == ".bmp":
            raise ValueError("Le fichier doit être au format .bmp")
    
        if not file.is_file():
            raise FileNotFoundError(f"Le fichier {file} n'existe pas.")
        
        img = Image.open(file)
        img = img.convert("RGB")
        pixels = list(img.getdata())
        block_size = int(self.params["rel_size"]*len(pixels))
        output = pixels[:]
        for _ in range(self.params["nb_swaps"]):
            start_first_block = random.randint(0, len(pixels) - block_size)
            start_second_block = random.randint(0, len(pixels) - block_size)
            while not(start_second_block + block_size < start_first_block or start_second_block > start_first_block + block_size):
                start_second_block = random.randint(0, len(pixels) - block_size)
            output[start_first_block:start_first_block+block_size], output[start_second_block:start_second_block+block_size] = \
            output[start_second_block:start_second_block+block_size],output[start_first_block:start_first_block+block_size]

        img_transformed = Image.new("RGB", img.size)
        img_transformed.putdata(output)
        img_transformed.save(self.out_dir / name_alt, "BMP")

class ReplaceImage(Action):
    """ Action de remplacer des blocs de pixels dans une image BMP. La taille des blocs en pourcentage de la taille de l'image est spécifiée
    par "rel_size" qui est un flottant compris entre 0 et 1 : 0.5 signifie qu'on remplace la moitié de l'image. 
    Le nombre d'ajouts est spécifié par "nb_add".
    Les blocs de pixels sont tirés aléatoirement si "source" est None (par défaut) ou tirés d'une image BMP dont le chemin d'accès 
    est "source" si celui-ci est spécifié.
    """
    def __init__(self, nb_add: int, rel_size: float, in_dir: Path, out_dir: Path, source: Path=None):
        params = {"nb_add" : nb_add, "rel_size" : rel_size, "source" : source}
        super().__init__("replace", params=params, in_dir=in_dir, out_dir=out_dir)
    
    def transform_and_save(self, file: Path, name_alt: str):
        if not file.suffix.lower() == ".bmp":
            raise ValueError("Le fichier doit être au format .bmp")
    
        if not file.is_file():
            raise FileNotFoundError(f"Le fichier {file} n'existe pas.")
        
        img = Image.open(file)
        img = img.convert("RGB")
        pixels = list(img.getdata())
        block_size = int(self.params["rel_size"]*len(pixels))
        output = pixels[:]
        if self.params["source"] != None:
            src = Image.open(self.params["source"])
            src = src.convert("RGB")
            pixels_src = list(src.getdata())
        for _ in range(self.params["nb_add"]):
            start_block = random.randint(0, len(pixels) - block_size)
            if self.params["source"] == None:
                block = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(block_size)]
            else:
                start_block_source = random.randint(0,len(pixels_src) - block_size)
                block = pixels_src[start_block_source:start_block_source + block_size]

            output[start_block:start_block+block_size] = block
        img_transformed = Image.new("RGB", img.size)
        img_transformed.putdata(output)
        img_transformed.save(self.out_dir / name_alt, "BMP")

class AddText(Action):
    """Rallonge un texte en ajoutant nb_add blocs de taille rel_size*len(texte) à un texte.
    L'ajout est par défaut composé de caractères ASCII aléatoires mais peut être tiré d'un fichier texte
    dont le chemin d'accès est spécifié par la variable "source".
    """
    def __init__(self, nb_add: int, rel_size: float, in_dir: Path, out_dir: Path, source: Path=None):
            params = {"nb_add" : nb_add, "rel_size" : rel_size, "source" : source}
            super().__init__("add", params=params, in_dir=in_dir, out_dir=out_dir)
    def transform_and_save(self, file: Path, name_alt: str):
        if not file.suffix.lower() == ".txt":
            raise ValueError("Le fichier doit être au format .txt")
    
        if not file.is_file():
            raise FileNotFoundError(f"Le fichier {file} n'existe pas.")
        
        with file.open("r", encoding="utf-8") as fichier:
            content = fichier.read()

        block_size = int(self.params["rel_size"]*len(content))

        if self.params["source"] != None:
            with self.params["source"].open("r", encoding="utf-8") as source_file:
                src = source_file.read()

        for _ in range(self.params["nb_add"]):
            start = random.randint(0,len(content))
            if self.params["source"] == None:
                random_chars = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=block_size)) 
                content = content[:start] + random_chars + content[start:]
            else:
                start_source = random.randint(0,len(src))
                content = content[:start] + src[start_source:start_source + block_size] + content[start:]
        out_path = self.out_dir /  name_alt
        with out_path.open("w", encoding="utf-8") as file:
            file.write(content)

class SwapText(Action):
    """
    Action de swap: échange des parties d'un texte .txt. Réalise nb_swaps échanges aléatoires 
    avec des blocs de taille rel_size*len(image): rel_size est un flottant entre 0 et 1 qui
    représente la taille des blocs à échanger en pourcentage de la longueur du fichier. Ce paramètre 
    doit être inférieur à 1/3.
    """
    def __init__(self, nb_swaps: int, rel_size: float, in_dir: Path, out_dir: Path):
        if rel_size > 1/3:
            raise ValueError(f"La taille des blocs échangés doit être inférieure au tiers du fichier (ici rel_size état {rel_size})")
        params = {"nb_swaps" : nb_swaps, "rel_size" : rel_size}
        super().__init__(name="Swap", params=params, in_dir=in_dir, out_dir=out_dir)
    def transform_and_save(self, file: Path, name_alt: str):
        if not file.suffix.lower() == ".txt":
            raise ValueError("Le fichier doit être au format .txt")
    
        if not file.is_file():
            raise FileNotFoundError(f"Le fichier {file} n'existe pas.")

        with file.open("r", encoding="utf-8") as fichier:
                content = list(fichier.read())

        block_size = int(self.params["rel_size"]*len(content))
        for _ in range(self.params["nb_swaps"]):
            start_first_block = random.randint(0, len(content) - block_size)
            start_second_block = random.randint(0, len(content) - block_size)
            while not(start_second_block + block_size < start_first_block or start_second_block > start_first_block + block_size):
                start_second_block = random.randint(0, len(content) - block_size)
            content[start_first_block:start_first_block+block_size], content[start_second_block:start_second_block+block_size] = \
            content[start_second_block:start_second_block+block_size],content[start_first_block:start_first_block+block_size]


        out_path = self.out_dir /  name_alt
        with out_path.open("w", encoding="utf-8") as file:
            file.write("".join(content))

def main():
    in_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])

    # imswapper = SwapImage(nb_swaps=5, rel_size=0.05, in_dir=in_dir, out_dir=out_dir)
    # imswapper.generate_benchmark()

    # source_image = Path("C:/Users/defir/Documents/tests/ajout.bmp")
    # imreplacer = ReplaceImage(nb_add=5, rel_size=0.05, in_dir=in_dir, out_dir=out_dir, source=source_image)
    # imreplacer.generate_benchmark()

    # source_texte = Path("C:/Users/defir/Documents/tests/ajout.txt")
    # text_adder = AddText(nb_add=5, rel_size=0.05, in_dir=in_dir, out_dir=out_dir, source=source_texte)
    # text_adder.generate_benchmark()

    text_swapper = SwapText(nb_swaps=5, rel_size=0.05, in_dir=in_dir, out_dir=out_dir)
    text_swapper.generate_benchmark()


if __name__ == '__main__':
    main()

