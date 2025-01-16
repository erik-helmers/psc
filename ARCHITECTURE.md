# Architecture du projet

> TODO: trouver un nom sympa 

Le projet est conçu autour des composantes suivantes : 
 - `lib` : toute la logique essentielle est dedans, c'est `lib` qui sait lancer des tests, stocker et faire l'analyse préliminaire des résultats.
 - `runners` : tous les algorithmes disponibles depuis `lib`
 - `fuzzylib` : diverses implémentation (en Rust, btw) pour avoir des implémentations rapides.
 - `benchgen` : génération déterministe de banques de tests
 - `notebooks` : TODO
    
