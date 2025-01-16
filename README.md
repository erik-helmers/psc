# Plateforme de test


## Getting started

Pour simplifier la vie de tout le monde, le projet dépend sur `uv` ([installer ici](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)).
`uv` s'occupe d'installer une version correcte de Python, les dépendences, etc. 
Dans ces conditions, tout passe par `uv` et pas par `pip`, `cond`, `pyenv`, `poetry` ou autre.

Il faut installer les bindings avec `maturin` (installé automatiquement par `uv`) : 

``` sh
source .venv/bin/activate
cd fuzzylib/bindings
maturin develop --uv 
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

- Pour lancer l'interface web : 
    ```sh
    #TODO:
    ```

- Pour un REPL : 

``` sh
uv run ipython
```

