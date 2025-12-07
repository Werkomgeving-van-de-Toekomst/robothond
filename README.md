# Unitree Go2 EDU Development Project

Ontwikkelproject voor de Unitree Go2 EDU robot.

## Vereisten

- Python 3.8 of hoger
- Netwerkverbinding met de Go2 EDU robot
- Unitree Go2 EDU robot met ontwikkelaarsmodus ingeschakeld

## Installatie

1. Clone dit repository of download de bestanden

2. Maak een virtual environment aan (aanbevolen):
```bash
python3 -m venv venv
source venv/bin/activate  # Op macOS/Linux
# of: venv\Scripts\activate  # Op Windows
```

3. Installeer de benodigde dependencies:
```bash
pip install -r requirements.txt
```

3. Configureer de verbinding met je robot in `config/robot_config.yaml`

## Projectstructuur

```
unitreego2/
├── src/                    # Hoofdcode
│   ├── unitree_go2/       # Unitree Go2 SDK wrapper
│   └── examples/          # Voorbeeldscripts
├── config/                # Configuratiebestanden
├── tests/                 # Unit tests
│   ├── test_connection.py    # Verbinding tests
│   ├── test_commands.py      # Commando tests
│   ├── test_sensors.py       # Sensor tests
│   ├── test_error_handling.py # Error handling tests
│   └── test_performance.py   # Performance tests
├── docs/                  # Documentatie
├── run_tests.py           # Test runner script
└── requirements.txt       # Python dependencies
```

## Gebruik

### Eerste keer opzetten

1. **Diagnostiek uitvoeren** (aanbevolen als eerste stap):
```bash
python src/examples/diagnostics.py -i 192.168.123.161
```

2. **Automatisch testen** (aanbevolen - wacht op robot en voert tests uit):
```bash
# Wacht op robot en voer alle tests uit
python auto_test.py

# Met custom IP adres
python auto_test.py -i 192.168.123.161

# Continue modus (herhaalt tests elke minuut)
python auto_test.py --continuous
```

3. **Handmatig tests uitvoeren**:
```bash
# Alle tests
python run_tests.py

# Specifieke test categorie
python run_tests.py -c connection -c commands

# Met custom IP adres
python run_tests.py -i 192.168.123.161

# Verbose output
python run_tests.py -v
```

### Basis verbinding

```python
from src.unitree_go2 import Go2Robot

robot = Go2Robot(ip_address="192.168.123.161")
robot.connect()
```

### Voorbeelden uitvoeren

```bash
# Basis beweging
python src/examples/basic_movement.py

# Sensor data lezen
python src/examples/read_sensors.py

# Diagnostiek
python src/examples/diagnostics.py
```

## Documentatie

Voor volledige API documentatie, zie: https://support.unitree.com/home/en/developer

## Licentie

Dit project is voor educatieve doeleinden.

