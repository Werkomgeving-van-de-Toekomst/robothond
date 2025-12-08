# Unitree Go2 EDU Handleiding

Nederlandse handleiding voor de Unitree Go2 EDU robot.

## Inhoudsopgave

1. [Inleiding](#inleiding)
2. [Eerste Stappen](#eerste-stappen)
3. [Robot Configuratie](#robot-configuratie)
4. [Basis Operaties](#basis-operaties)
5. [Bewegingscommando's](#bewegingscommando's)
6. [Sensor Data](#sensor-data)
7. [Veiligheid](#veiligheid)
8. [Troubleshooting](#troubleshooting)

## Inleiding

De Unitree Go2 EDU is een geavanceerde viervoetige robot (quadruped) ontwikkeld voor educatieve en onderzoeksdoeleinden. Deze handleiding helpt je om te beginnen met het programmeren en besturen van de Go2 robot.

### Belangrijke Kenmerken

- **12 Actuatoren**: 3 per been (heup, dij, kuit)
- **IMU Sensor**: Voor oriëntatie en versnelling
- **Camera**: Visuele waarneming
- **WiFi Communicatie**: Via UDP protocol
- **SDK Ondersteuning**: Python, C++, ROS2

### Systeemvereisten

- Python 3.8 of hoger
- Netwerkverbinding (WiFi of Ethernet)
- Unitree Go2 EDU robot met ontwikkelaarsmodus ingeschakeld
- Computer op hetzelfde netwerk als de robot

## Eerste Stappen

### 1. Robot Aansluiten

1. **Zet de robot aan**: Druk op de aan/uit knop
2. **Wacht op opstarten**: Robot start op en gaat in stand-by modus
3. **Controleer WiFi**: Robot maakt verbinding met WiFi netwerk
4. **Vind IP adres**: Standaard IP is `192.168.123.161`

### 2. Netwerk Configuratie

De robot gebruikt standaard deze instellingen:
- **IP Adres**: `192.168.123.161`
- **Poort**: `8080` (UDP)
- **Subnet**: `192.168.123.0/24`

Zorg dat je computer op hetzelfde netwerk zit.

### 3. Verbinding Testen

```bash
# Test verbinding met ping
ping 192.168.123.161

# Of gebruik het diagnostiek script
python src/examples/diagnostics.py -i 192.168.123.161
```

## Robot Configuratie

### Configuratiebestand

Pas `config/robot_config.yaml` aan:

```yaml
robot:
  ip_address: "192.168.123.161"
  sdk_port: 8080
  timeout: 5.0

movement:
  default_speed: 0.5
  default_angular_velocity: 0.5

sensors:
  update_rate: 20
  enabled:
    - imu
    - joint_states
    - battery

safety:
  max_speed: 1.0
  emergency_stop_enabled: true
```

### Python Configuratie Laden

```python
from src.unitree_go2.config import load_config

config = load_config("config/robot_config.yaml")
ip_address = config["robot"]["ip_address"]
```

## Basis Operaties

### Verbinding Maken

```python
from src.unitree_go2 import Go2Robot

# Maak verbinding
robot = Go2Robot(ip_address="192.168.123.161")
robot.connect()

# Gebruik context manager (aanbevolen)
with Go2Robot(ip_address="192.168.123.161") as robot:
    # Je code hier
    pass
```

### Basis Commando's

```python
# Sta op
robot.stand()

# Ga zitten
robot.sit()

# Stop beweging
robot.stop()

# Haal status op
state = robot.get_state()
```

## Bewegingscommando's

### Basis Beweging

De robot beweegt met snelheidscommando's:

```python
# Beweeg vooruit
robot.move(vx=0.3, vy=0.0, vyaw=0.0)

# Beweeg achteruit
robot.move(vx=-0.3, vy=0.0, vyaw=0.0)

# Draai links
robot.move(vx=0.0, vy=0.0, vyaw=0.5)

# Draai rechts
robot.move(vx=0.0, vy=0.0, vyaw=-0.5)

# Diagonaal bewegen
robot.move(vx=0.3, vy=0.2, vyaw=0.1)
```

### Parameters

- **vx**: Snelheid vooruit/achteruit (m/s)
  - Positief = vooruit
  - Negatief = achteruit
  - Bereik: -1.0 tot 1.0 m/s

- **vy**: Snelheid links/rechts (m/s)
  - Positief = rechts
  - Negatief = links
  - Bereik: -1.0 tot 1.0 m/s

- **vyaw**: Draaisnelheid (rad/s)
  - Positief = tegen de klok in
  - Negatief = met de klok mee
  - Bereik: -1.0 tot 1.0 rad/s

### Bewegingspatronen

```python
import time

# Loop vooruit voor 3 seconden
robot.move(vx=0.3, vy=0.0, vyaw=0.0)
time.sleep(3.0)
robot.stop()

# Cirkelbeweging
robot.move(vx=0.3, vy=0.0, vyaw=0.3)
time.sleep(5.0)
robot.stop()
```

## Sensor Data

### Status Ophalen

```python
state = robot.get_state()

# Beschikbare data:
# - joint_positions: Posities van alle joints
# - joint_velocities: Snelheden van alle joints
# - base_position: Basis positie (x, y, z)
# - base_orientation: Basis oriëntatie (quaternion)
# - base_linear_velocity: Lineaire snelheid
# - base_angular_velocity: Hoeksnelheid
# - imu_data: IMU sensor data
# - battery_level: Batterij niveau
```

### Voorbeeld: Sensor Data Lezen

```python
from src.examples.read_sensors import read_sensors

# Lees sensor data
read_sensors(robot_ip="192.168.123.161")
```

## Veiligheid

### Belangrijke Veiligheidsregels

1. **Emergency Stop**: Zorg altijd voor een manier om snel te stoppen
2. **Test Eerst**: Test commando's eerst met lage snelheden
3. **Voldoende Ruimte**: Zorg voor voldoende ruimte rondom de robot
4. **Stabiele Ondergrond**: Gebruik vlakke, stabiele ondergrond
5. **Monitoring**: Houd de robot altijd in de gaten tijdens operatie

### Emergency Stop

```python
# Stop alle beweging direct
robot.stop()

# Of disconnect
robot.disconnect()
```

### Veiligheidslimieten

- **Maximale snelheid**: 1.0 m/s (configureerbaar)
- **Maximale draaisnelheid**: 1.0 rad/s
- **Minimale batterij**: 20% (robot gaat automatisch zitten)

## Troubleshooting

### Verbindingsproblemen

**Probleem**: Kan niet verbinden met robot

**Oplossingen**:
1. Check IP adres: `ping 192.168.123.161`
2. Check netwerk: Zit je op hetzelfde netwerk?
3. Check firewall: Staat poort 8080 open?
4. Check robot status: Is robot aan en verbonden?

### Bewegingsproblemen

**Probleem**: Robot beweegt niet

**Oplossingen**:
1. Check of robot rechtop staat: `robot.stand()`
2. Check snelheid: Gebruik lage snelheden eerst
3. Check ondergrond: Is ondergrond vlak?
4. Check batterij: Is batterij voldoende opgeladen?

### Sensor Problemen

**Probleem**: Geen sensor data

**Oplossingen**:
1. Check verbinding: Is robot verbonden?
2. Check configuratie: Zijn sensoren ingeschakeld?
3. Check update rate: Is update rate niet te hoog?

## Best Practices

1. **Gebruik Context Manager**: Altijd `with` statement gebruiken
2. **Error Handling**: Gebruik try/except voor commando's
3. **Logging**: Log belangrijke acties
4. **Testing**: Test eerst met kleine bewegingen
5. **Documentatie**: Documenteer je code

## Voorbeelden

Zie `src/examples/` voor complete voorbeelden:
- `basic_movement.py`: Basis beweging
- `read_sensors.py`: Sensor data lezen
- `diagnostics.py`: Diagnostiek uitvoeren

## Referenties

- [Go2 SDK Referentie](./GO2_SDK_REFERENTIE.md)
- [Go2 SDK Repositories](./GO2_SDK_REPOSITORIES.md) - Officiële GitHub repositories
- [Unitree Developer Documentation](https://support.unitree.com/home/en/developer)
- [Go2 URDF Repository](https://github.com/Unitree-Go2-Robot/go2_description)
- [Project README](../README.md)

## Officiële SDK Repositories

- **unitree_sdk2**: https://github.com/unitreerobotics/unitree_sdk2 (C++ SDK)
- **unitree_sdk2_python**: https://github.com/unitreerobotics/unitree_sdk2_python (Python wrapper)
- **unitree_ros2**: https://github.com/unitreerobotics/unitree_ros2 (ROS2 pakket)

Zie [GO2_SDK_REPOSITORIES.md](./GO2_SDK_REPOSITORIES.md) voor volledige details.

## Ondersteuning

Voor vragen of problemen:
1. Check de troubleshooting sectie
2. Bekijk de voorbeelden in `src/examples/`
3. Raadpleeg de officiële Unitree documentatie

