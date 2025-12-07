# PyBullet Setup Instructies

PyBullet vereist Python 3.8-3.11. Dit project heeft een aparte virtual environment voor PyBullet simulatie.

## Setup PyBullet Environment

### Stap 1: Maak PyBullet virtual environment

```bash
# Gebruik Python 3.11 (of 3.8-3.11)
python3.11 -m venv venv_pybullet
```

### Stap 2: Activeer environment

```bash
source venv_pybullet/bin/activate
```

### Stap 3: Installeer dependencies

**Methode 1: Via pip (als pre-built wheels beschikbaar zijn)**

```bash
# Upgrade pip eerst
pip install --upgrade pip

# Probeer PyBullet te installeren
pip install pybullet numpy
```

**Methode 2: Via conda (aanbevolen als pip faalt)**

```bash
# Installeer conda als je het nog niet hebt
# Dan:
conda create -n pybullet python=3.11
conda activate pybullet
conda install -c conda-forge pybullet numpy
```

**Methode 3: Pre-built binaries**

Download PyBullet pre-built binaries van de officiële website en installeer handmatig.

**Let op**: PyBullet vereist mogelijk compilatie tools (C++ compiler, CMake, etc.). Als installatie faalt, gebruik conda of wacht tot pre-built wheels beschikbaar zijn voor jouw platform.

**⚠️ Bekend Probleem**: Op macOS ARM64 (Apple Silicon) met Python 3.11 werkt pip install niet. Gebruik **Conda** (zie hieronder) of wacht op pre-built wheels.

### Conda Installatie (Aanbevolen voor macOS ARM64)

```bash
# Installeer Miniconda eerst: https://docs.conda.io/en/latest/miniconda.html

# Maak conda environment
conda create -n pybullet python=3.9
conda activate pybullet

# Installeer PyBullet via conda-forge
conda install -c conda-forge pybullet numpy
```

Dit werkt gegarandeerd op macOS ARM64!

## Gebruik

### PyBullet simulatie uitvoeren

```bash
# Activeer PyBullet environment
source venv_pybullet/bin/activate

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
source venv_pybullet/bin/activate
```

## Verificatie

Test of PyBullet correct is geïnstalleerd:

```bash
source venv_pybullet/bin/activate
python -c "import pybullet; print('PyBullet versie:', pybullet.__version__)"
```

## Troubleshooting

### PyBullet niet gevonden

- Zorg dat je de juiste virtual environment hebt geactiveerd: `source venv_pybullet/bin/activate`
- Controleer Python versie: `python --version` (moet 3.8-3.11 zijn)
- Herinstalleer: `pip install --upgrade pybullet`

### Import errors

- Zorg dat alle dependencies geïnstalleerd zijn: `pip install -r requirements_pybullet.txt`
- Controleer of je in de juiste directory bent: `cd /Users/marc/Projecten/unitreego2`

## Waarom aparte environment?

PyBullet ondersteunt momenteel Python 3.8-3.11, terwijl het hoofdproject Python 3.14 gebruikt. Door een aparte environment te gebruiken kunnen beide naast elkaar bestaan zonder conflicten.

