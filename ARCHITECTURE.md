# Architecture du projet

> TODO: trouver un nom sympa 

Le projet est conçu autour des composantes suivantes : 
 - `lib` : toute la logique essentielle est dedans, c'est `lib` qui sait lancer des tests, 
   stocker et partager les résultats.
 - `cli` : une interface toute simple pour utilisation depuis un terminal
 - `web` : version web qui permet d'explorer les résultats à partir de lib
 - `fuzzylib` : diverses implémentation (en Rust, btw) pour avoir une base 
    de tests corrects.
    
    
