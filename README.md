# Plateforme de test


## Getting started

Pour simplifier la vie de tout le monde, le projet dépend sur `uv` ([installer ici](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)).
`uv` s'occupe d'installer une version correcte de Python, les dépendences, etc. 
Dans ces conditions, tout passe par `uv` et pas par `pip`, `cond`, `pyenv`, `poetry` ou autre.



Commmencer par télécharger le projet : 
``` sh
git clone https://github.com/erik-helmers/psc 
cd psc
```


Il faut installer les bindings avec `maturin` (installé automatiquement par `uv`) : 

``` sh
uv sync
source .venv/bin/activate
```

Deux options pour installer `fuzzlib` : 

- Avec les builds Github : 
    - Télécharger le fichier correct pour votre système d'exploitation depuis les [actions](https://github.com/erik-helmers/psc/actions)
    - Dézipper l'archive dans `psc/wheels` (créer le dossier si besoin)
    - Ajouter en tant que dépendence : 
    ```sh
     uv add wheels-fuzzylib-1.0-cp311-cp311*
    ```
- Avec Rust installé ([installer ici](https://www.rust-lang.org/tools/install))
    ``` sh
    cd   fuzzylib/bindings
    maturin develop --uv 
    ```


Générer les benchmarks : 
``` sh
# Créations des dossiers 
mkdir -p data/benchmarks/{image,text} 
# Génération des benchmarks
uv run ./benchgen/image.py data/benchmarks/image  benchgen/image/*
uv run ./benchgen/text.py  data/benchmarks/text   benchgen/text/{proposition.ref.txt,*}
```

Vérifier que tout fonctionne en lançant une console : 
``` sh
uv run ipython 
```
``` ipython
In [1]: import fuzzylib

In [2]: fuzzylib.ssdeep.batch_hash
Out[2]: <function ssdeep.batch_hash(pairs)>
```

## Build, run, debug

- Pour lancer jupyter : 
    ```sh
    uv run jupyter lab . 
    ```

- Pour un REPL : 

``` sh
uv run ipython
```

