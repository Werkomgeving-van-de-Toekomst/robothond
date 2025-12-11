# Unitree Go2 EDU Development Project

Ontwikkelproject voor de Unitree Go2 EDU robot, gebaseerd op de officiële SDK.

## Vereisten

- Python 3.8-3.12 (3.12 aanbevolen)
- CycloneDDS (voor officiële SDK)
- Netwerkverbinding met de Go2 EDU robot
- Unitree Go2 EDU robot met ontwikkelaarsmodus ingeschakeld

## Installatie

### Stap 1: Clone repository

```bash
git clone <repository-url>
cd unitreego2
```

### Stap 2: Maak virtual environment

```bash
# Gebruik Python 3.12 voor beste compatibiliteit
python3.12 -m venv venv
source venv/bin/activate
```

### Stap 3: Installeer CycloneDDS

```bash
# Automatisch (aanbevolen)
./install_cyclonedds_macos.sh

# Of handmatig - zie docs/OFFICIELE_SDK_INTEGRATIE.md
```

### Stap 4: Installeer dependencies

```bash
pip install -r requirements.txt
```

### Stap 5: Test setup

```bash
python src/examples/first_time_setup_test.py --skip-robot
```

## Gebruik

### Basis verbinding

```python
from src.unitree_go2 import Go2Robot

# Verbind met robot (officiële SDK)
with Go2Robot(
    ip_address="192.168.123.161",
    network_interface="en0"  # macOS WiFi, of "eth0" voor Linux
) as robot:
    robot.stand()
    robot.move(vx=0.3, vy=0.0, vyaw=0.0)
    time.sleep(2)
    robot.stop()
    robot.sit()
```

### Voorbeelden uitvoeren

```bash
# First time setup test
python src/examples/first_time_setup_test.py

# Basis beweging
python src/examples/basic_movement.py -i 192.168.123.161 --interface en0

# Diagnostiek
python src/examples/diagnostics.py -i 192.168.123.161 --interface en0

# Voice control
python src/examples/voice_control.py --robot-ip 192.168.123.161
```

### Automatisch testen

```bash
# Wacht op robot en voer tests uit
python auto_test.py -i 192.168.123.161 --interface en0

# Continue modus
python auto_test.py --continuous
```

## Projectstructuur

```
unitreego2/
├── src/
│   ├── unitree_go2/       # SDK wrapper (officiële SDK)
│   ├── examples/          # Voorbeeldscripts
│   ├── voice/             # Voice control
│   └── simulation/        # PyBullet simulatie
├── docs/                  # Documentatie
├── tests/                 # Unit tests
├── config/                # Configuratie
├── flows/                 # Robot actie flows
└── unitree_sdk2_python/   # Officiële SDK
```

## Documentatie

Zie de `docs/` folder voor gedetailleerde documentatie:

- [First Time Setup](docs/FIRST_TIME_SETUP.md)
- [Officiële SDK Integratie](docs/OFFICIELE_SDK_INTEGRATIE.md)
- [Netwerk Verbinding](docs/NETWERK_OVERZICHT.md)
- [Voice Control](docs/VOICE_CONTROL.md)
- [Alle documentatie](docs/README.md)

## Licentie

Dit project is voor educatieve doeleinden.
