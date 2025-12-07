# PyBullet Setup Instructies

PyBullet vereist Python 3.8-3.11. Dit project gebruikt Conda voor PyBullet simulatie.

## Setup PyBullet Environment

### Stap 1: Activeer conda environment

```bash
conda activate pybullet
```

### Stap 2: Verifieer installatie

```bash
python -c "import pybullet; print('PyBullet versie:', pybullet.__version__)"
```

## Gebruik

### PyBullet simulatie uitvoeren

```bash
# Activeer conda environment
conda activate pybullet

# Voer simulatie uit
python src/examples/pybullet_simulation.py basic
python src/examples/pybullet_simulation.py movement
python src/examples/pybullet_simulation.py sensor
```

### Wisselen tussen environments

```bash
# Voor normale SDK ontwikkeling
source venv/bin/activate

# Voor PyBullet simulatie
conda activate pybullet
```

## Verificatie

Test of PyBullet correct is geïnstalleerd:

```bash
conda activate pybullet
python -c "import pybullet; print('PyBullet versie:', pybullet.__version__)"
```

## Troubleshooting

### Conda niet gevonden

- Zorg dat conda in je PATH staat
- Voeg toe aan ~/.zshrc: `export PATH="$HOME/miniconda3/bin:$PATH"`
- Of gebruik: `source ~/miniconda3/etc/profile.d/conda.sh`

### PyBullet niet gevonden

- Zorg dat je de conda environment hebt geactiveerd: `conda activate pybullet`
- Controleer Python versie: `python --version` (moet 3.8-3.11 zijn)
- Herinstalleer: `conda install -c conda-forge pybullet --force-reinstall`

### Import errors

- Zorg dat je in de project directory bent: `cd /Users/marc/Projecten/unitreego2`
- Controleer of alle bestanden aanwezig zijn

## Waarom Conda?

PyBullet heeft pre-built binaries via conda-forge die werken op macOS ARM64 (Apple Silicon), terwijl pip installatie faalt op dit platform.
