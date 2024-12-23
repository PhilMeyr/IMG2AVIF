# IMG2AVIF

Un script simple pour convertir des images en format AVIF par lots.

## Caractéristiques

- Conversion d'images vers le format AVIF
- Support des formats d'entrée : JPG, JPEG, PNG, GIF, BMP, TIFF
- Support des fichiers RAW (DNG, NEF)
- Préservation des données EXIF (quand possible)
- Traitement par lots avec multi-threading
- Conservation des fichiers non-image dans le dossier de sortie

## Prérequis

- Python 3.11
- pipenv

## Installation

1. Clonez le dépôt :

```bash
git clone [url-du-repo]
cd IMG2AVIF
```

2. Installez les dépendances :

```bash
pipenv install
```

## Utilisation

1. Créez un dossier `input` dans le répertoire du projet
2. Placez vos images à convertir dans le dossier `input`
3. Exécutez le script :

```bash
pipenv run python main.py
```

Les images converties seront sauvegardées dans le dossier `output`.

## Notes

- Les données EXIF sont préservées quand possible, mais le support est limité pour les fichiers RAW
- Le script utilise 5 workers en parallèle pour optimiser la vitesse de conversion
- Les fichiers non-image sont copiés tels quels dans le dossier de sortie

## Structure des dossiers

```bash
IMG2AVIF/
├── input/          # Dossier pour les images source
├── output/         # Dossier pour les images converties
├── main.py         # Script principal
├── Pipfile         # Configuration pipenv
└── README.md       # Documentation
```
