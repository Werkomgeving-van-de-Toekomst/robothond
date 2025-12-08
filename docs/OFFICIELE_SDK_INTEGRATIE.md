# Officiële SDK Integratie

Deze guide beschrijft hoe je de officiële `unitree_sdk2_python` SDK kunt gebruiken in plaats van onze custom wrapper.

## Overzicht

We ondersteunen nu twee opties:

1. **Custom Wrapper** (`Go2Robot`): Simpele UDP wrapper (huidige implementatie)
2. **Officiële SDK** (`Go2RobotOfficial`): Volledige officiële SDK met DDS communicatie

## Installatie Officiële SDK

### Stap 1: Clone Repository

De officiële SDK staat al in `unitree_sdk2_python/` directory.

### Stap 2: Installeer Dependencies

```bash
pip install cyclonedds==0.10.2 numpy opencv-python
```

### Stap 3: Installeer SDK

```bash
cd unitree_sdk2_python
pip install -e .
```

**Op macOS**: Mogelijk moet je CycloneDDS eerst compileren:

```bash
# Installeer CycloneDDS
git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x
cd cyclonedds && mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
cmake --build . --target install

# Set environment variable
export CYCLONEDDS_HOME="~/cyclonedds/install"

# Installeer SDK
cd ../../unitree_sdk2_python
pip install -e .
```

## Gebruik Officiële SDK

### Basis Gebruik

```python
from src.unitree_go2 import Go2RobotOfficial

# Gebruik officiële SDK
robot = Go2RobotOfficial(
    ip_address="192.168.123.161",
    network_interface="en0"  # macOS WiFi interface
)

robot.connect()
robot.stand()
robot.move(vx=0.3, vy=0.0, vyaw=0.0)
robot.stop()
robot.disconnect()
```

### Automatische Interface Detectie

```python
# Laat SDK automatisch netwerk interface detecteren
robot = Go2RobotOfficial(ip_address="192.168.123.161")
robot.connect()  # Detecteert automatisch interface
```

### Context Manager

```python
with Go2RobotOfficial(ip_address="192.168.123.161") as robot:
    robot.stand()
    robot.move(vx=0.3, vy=0.0, vyaw=0.0)
    state = robot.get_state()
    print(f"Batterij: {state['battery_level']}%")
```

## Verschillen tussen Custom en Officiële SDK

### Custom Wrapper (`Go2Robot`)

**Voordelen**:
- ✅ Geen extra dependencies nodig
- ✅ Simpel UDP protocol
- ✅ Werkt direct met IP adres
- ✅ Geen CycloneDDS nodig

**Nadelen**:
- ❌ Beperkte functionaliteit
- ❌ Mogelijk niet volledig compatibel met alle robot features

### Officiële SDK (`Go2RobotOfficial`)

**Voordelen**:
- ✅ Volledige robot functionaliteit
- ✅ Officieel ondersteund door Unitree
- ✅ High-level en low-level controle
- ✅ Camera, audio, en andere features

**Nadelen**:
- ❌ Vereist CycloneDDS installatie
- ❌ Vereist netwerk interface naam (niet alleen IP)
- ❌ Meer complexe setup

## Welke te Gebruiken?

### Gebruik Custom Wrapper als:
- Je snel wilt beginnen zonder extra setup
- Je alleen basis beweging nodig hebt
- Je geen CycloneDDS wilt installeren

### Gebruik Officiële SDK als:
- Je volledige robot functionaliteit nodig hebt
- Je camera, audio, of andere features wilt gebruiken
- Je low-level motor controle nodig hebt
- Je officiële ondersteuning wilt

## Migratie van Custom naar Officiële SDK

De API is compatibel, dus je kunt eenvoudig wisselen:

```python
# Oude code (custom wrapper)
from src.unitree_go2 import Go2Robot
robot = Go2Robot(ip_address="192.168.123.161")

# Nieuwe code (officiële SDK)
from src.unitree_go2 import Go2RobotOfficial
robot = Go2RobotOfficial(ip_address="192.168.123.161", network_interface="en0")
```

De rest van je code blijft hetzelfde!

## Netwerk Interface Namen

### macOS
- WiFi: `en0`, `en1`
- Ethernet: `en2`, `en3`

Vind je interface:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### Linux
- Ethernet: `eth0`, `eth1`
- WiFi: `wlan0`, `wlan1`

Vind je interface:
```bash
ip route get 8.8.8.8 | grep -oP 'dev \K\S+'
```

## Troubleshooting

### "Officiële SDK niet gevonden"

Zorg dat `unitree_sdk2_python/` directory bestaat en geïnstalleerd is:
```bash
cd unitree_sdk2_python
pip install -e .
```

### "Could not locate cyclonedds"

Installeer CycloneDDS eerst (zie installatie instructies hierboven).

### "Network interface not found"

Geef expliciet netwerk interface op:
```python
robot = Go2RobotOfficial(
    ip_address="192.168.123.161",
    network_interface="en0"  # Pas aan naar jouw interface
)
```

### Verbinding werkt niet

1. Check of robot aan is
2. Check netwerk verbinding
3. Check firewall instellingen
4. Probeer andere netwerk interface

## Officiële SDK Voorbeelden

Bekijk voorbeelden in `unitree_sdk2_python/example/go2/`:

```bash
# High-level controle
python unitree_sdk2_python/example/go2/high_level/go2_sport_client.py en0

# Low-level controle
python unitree_sdk2_python/example/go2/low_level/go2_stand_example.py en0

# Camera
python unitree_sdk2_python/example/go2/front_camera/camera_opencv.py en0
```

## Referenties

- [Officiële SDK Repository](../unitree_sdk2_python/README.md)
- [Go2 Handleiding](./GO2_HANDLEIDING.md)
- [Go2 SDK Referentie](./GO2_SDK_REFERENTIE.md)

