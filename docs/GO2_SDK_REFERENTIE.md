# Unitree Go2 EDU SDK Referentie

Complete SDK referentie voor de Unitree Go2 EDU robot in het Nederlands.

## Inhoudsopgave

1. [Overzicht](#overzicht)
2. [Installatie](#installatie)
3. [API Referentie](#api-referentie)
4. [Commando's](#commando's)
5. [Data Structuren](#data-structuren)
6. [Fouten en Exceptions](#fouten-en-exceptions)
7. [Voorbeelden](#voorbeelden)

## Overzicht

De Unitree Go2 EDU SDK biedt een Python interface voor het programmeren en besturen van de Go2 robot. De SDK communiceert via UDP met de robot op poort 8080.

### Architectuur

```
┌─────────────┐         UDP          ┌─────────────┐
│   Python    │  ←──────────────→    │   Go2 Robot │
│   Script    │    Port 8080         │             │
└─────────────┘                       └─────────────┘
```

### Communicatie Protocol

- **Protocol**: UDP (User Datagram Protocol)
- **Poort**: 8080 (standaard)
- **Data Format**: JSON
- **Encoding**: UTF-8

## Installatie

### Vereisten

```bash
pip install numpy protobuf websocket-client requests pyyaml
```

### Installatie uit Repository

```bash
git clone <repository-url>
cd unitreego2
pip install -r requirements.txt
```

## API Referentie

### Go2Robot Klasse

De hoofdklasse voor interactie met de Go2 robot.

#### Initialisatie

```python
Go2Robot(
    ip_address: str = "192.168.123.161",
    port: int = 8080,
    timeout: float = 5.0
)
```

**Parameters**:
- `ip_address` (str): IP adres van de robot
- `port` (int): UDP poort (standaard: 8080)
- `timeout` (float): Timeout in seconden voor commando's

**Voorbeeld**:
```python
robot = Go2Robot(
    ip_address="192.168.123.161",
    port=8080,
    timeout=5.0
)
```

#### Methoden

##### `connect() -> bool`

Maak verbinding met de robot.

**Returns**:
- `bool`: True als verbinding succesvol is

**Raises**:
- `Go2ConnectionError`: Als verbinding mislukt

**Voorbeeld**:
```python
try:
    robot.connect()
    print("Verbonden!")
except Go2ConnectionError as e:
    print(f"Verbindingsfout: {e}")
```

##### `disconnect()`

Verbreek verbinding met de robot.

**Voorbeeld**:
```python
robot.disconnect()
```

##### `stand()`

Laat robot rechtop staan.

**Returns**:
- `Dict[str, Any]`: Antwoord van robot

**Voorbeeld**:
```python
result = robot.stand()
print(result)  # {"status": "ok", "message": "Command sent"}
```

##### `sit()`

Laat robot zitten.

**Returns**:
- `Dict[str, Any]`: Antwoord van robot

**Voorbeeld**:
```python
robot.sit()
```

##### `move(vx: float, vy: float, vyaw: float)`

Beweeg robot met opgegeven snelheden.

**Parameters**:
- `vx` (float): Snelheid vooruit/achteruit (m/s)
  - Positief = vooruit
  - Negatief = achteruit
  - Bereik: -1.0 tot 1.0
- `vy` (float): Snelheid links/rechts (m/s)
  - Positief = rechts
  - Negatief = links
  - Bereik: -1.0 tot 1.0
- `vyaw` (float): Draaisnelheid (rad/s)
  - Positief = tegen de klok in
  - Negatief = met de klok mee
  - Bereik: -1.0 tot 1.0

**Returns**:
- `Dict[str, Any]`: Antwoord van robot

**Voorbeeld**:
```python
# Beweeg vooruit
robot.move(vx=0.3, vy=0.0, vyaw=0.0)

# Draai terwijl je vooruit beweegt
robot.move(vx=0.3, vy=0.0, vyaw=0.2)
```

##### `stop()`

Stop alle beweging.

**Returns**:
- `Dict[str, Any]`: Antwoord van robot

**Voorbeeld**:
```python
robot.stop()
```

##### `get_state() -> Dict[str, Any]`

Haal robot status op.

**Returns**:
- `Dict[str, Any]`: Robot status met:
  - `joint_positions`: Dict met joint posities
  - `joint_velocities`: Dict met joint snelheden
  - `base_position`: [x, y, z] positie
  - `base_orientation`: [w, x, y, z] quaternion
  - `base_linear_velocity`: [vx, vy, vz] lineaire snelheid
  - `base_angular_velocity`: [wx, wy, wz] hoeksnelheid
  - `imu_data`: IMU sensor data
  - `battery_level`: Batterij niveau (0-100)

**Voorbeeld**:
```python
state = robot.get_state()
print(f"Batterij: {state['battery_level']}%")
print(f"Positie: {state['base_position']}")
```

##### `send_command(command: Dict[str, Any]) -> Dict[str, Any]`

Verstuur een custom commando naar de robot.

**Parameters**:
- `command` (Dict[str, Any]): Commando dictionary

**Returns**:
- `Dict[str, Any]`: Antwoord van robot

**Voorbeeld**:
```python
command = {
    "command": "custom_action",
    "params": {"value": 123}
}
result = robot.send_command(command)
```

#### Context Manager

De `Go2Robot` klasse ondersteunt context manager protocol:

```python
with Go2Robot(ip_address="192.168.123.161") as robot:
    robot.stand()
    robot.move(vx=0.3, vy=0.0, vyaw=0.0)
    # Automatisch disconnect bij exit
```

## Commando's

### Basis Commando's

#### Stand Commando

```python
{
    "command": "stand",
    "mode": "stand"
}
```

#### Sit Commando

```python
{
    "command": "sit",
    "mode": "sit"
}
```

#### Move Commando

```python
{
    "command": "move",
    "vx": 0.3,      # m/s
    "vy": 0.0,      # m/s
    "vyaw": 0.0     # rad/s
}
```

#### Get State Commando

```python
{
    "command": "get_state"
}
```

## Data Structuren

### Joint Namen

De Go2 heeft 12 joints (3 per been):

**Front Left (FL)**:
- `FL_hip_joint`
- `FL_thigh_joint`
- `FL_calf_joint`

**Front Right (FR)**:
- `FR_hip_joint`
- `FR_thigh_joint`
- `FR_calf_joint`

**Rear Left (RL)**:
- `RL_hip_joint`
- `RL_thigh_joint`
- `RL_calf_joint`

**Rear Right (RR)**:
- `RR_hip_joint`
- `RR_thigh_joint`
- `RR_calf_joint`

### State Dictionary Structuur

```python
{
    "joint_positions": {
        "FL_hip_joint": 0.0,
        "FL_thigh_joint": 0.4,
        "FL_calf_joint": -0.8,
        # ... andere joints
    },
    "joint_velocities": {
        "FL_hip_joint": 0.0,
        # ... andere joints
    },
    "base_position": [0.0, 0.0, 0.4],  # x, y, z in meters
    "base_orientation": [1.0, 0.0, 0.0, 0.0],  # w, x, y, z quaternion
    "base_linear_velocity": [0.0, 0.0, 0.0],  # vx, vy, vz in m/s
    "base_angular_velocity": [0.0, 0.0, 0.0],  # wx, wy, wz in rad/s
    "imu_data": {
        "acceleration": [0.0, 0.0, -9.81],
        "angular_velocity": [0.0, 0.0, 0.0],
        "orientation": [1.0, 0.0, 0.0, 0.0]
    },
    "battery_level": 85  # 0-100
}
```

## Fouten en Exceptions

### Exception Hiërarchie

```
Exception
└── Go2Exception (basis exception)
    ├── Go2ConnectionError (verbindingsfouten)
    ├── Go2CommandError (commando fouten)
    └── Go2TimeoutError (timeout fouten)
```

### Go2ConnectionError

Gegooid wanneer verbinding met robot mislukt.

**Voorbeeld**:
```python
try:
    robot.connect()
except Go2ConnectionError as e:
    print(f"Kon niet verbinden: {e}")
```

### Go2CommandError

Gegooid wanneer commando niet succesvol is.

**Voorbeeld**:
```python
try:
    robot.move(vx=2.0, vy=0.0, vyaw=0.0)  # Te hoge snelheid
except Go2CommandError as e:
    print(f"Commando fout: {e}")
```

### Go2TimeoutError

Gegooid wanneer timeout optreedt.

**Voorbeeld**:
```python
try:
    state = robot.get_state()
except Go2TimeoutError as e:
    print(f"Timeout: {e}")
```

## Voorbeelden

### Basis Gebruik

```python
from src.unitree_go2 import Go2Robot

# Verbind met robot
with Go2Robot(ip_address="192.168.123.161") as robot:
    # Sta op
    robot.stand()
    
    # Beweeg vooruit
    robot.move(vx=0.3, vy=0.0, vyaw=0.0)
    
    # Wacht 3 seconden
    import time
    time.sleep(3.0)
    
    # Stop
    robot.stop()
    
    # Ga zitten
    robot.sit()
```

### Sensor Data Lezen

```python
from src.unitree_go2 import Go2Robot

with Go2Robot() as robot:
    # Haal status op
    state = robot.get_state()
    
    # Print batterij niveau
    print(f"Batterij: {state['battery_level']}%")
    
    # Print positie
    pos = state['base_position']
    print(f"Positie: x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f}")
    
    # Print joint posities
    for joint, position in state['joint_positions'].items():
        print(f"{joint}: {position:.3f} rad")
```

### Bewegingspatroon

```python
from src.unitree_go2 import Go2Robot
import time

with Go2Robot() as robot:
    robot.stand()
    time.sleep(2.0)
    
    # Vierkant patroon
    for _ in range(4):
        # Beweeg vooruit
        robot.move(vx=0.3, vy=0.0, vyaw=0.0)
        time.sleep(2.0)
        
        # Stop
        robot.stop()
        time.sleep(0.5)
        
        # Draai 90 graden
        robot.move(vx=0.0, vy=0.0, vyaw=0.5)
        time.sleep(3.14 / 0.5)  # 90 graden = π/2 rad
    
    robot.stop()
    robot.sit()
```

### Error Handling

```python
from src.unitree_go2 import Go2Robot, Go2ConnectionError, Go2CommandError

try:
    robot = Go2Robot(ip_address="192.168.123.161")
    robot.connect()
    
    robot.stand()
    robot.move(vx=0.3, vy=0.0, vyaw=0.0)
    
except Go2ConnectionError as e:
    print(f"Verbindingsfout: {e}")
except Go2CommandError as e:
    print(f"Commando fout: {e}")
finally:
    robot.disconnect()
```

## Best Practices

1. **Gebruik Context Manager**: Altijd `with` statement
2. **Error Handling**: Gebruik try/except
3. **Timeouts**: Stel realistische timeouts in
4. **Snelheden**: Begin met lage snelheden
5. **Testing**: Test eerst zonder robot (simulatie)

## Referenties

- [Go2 Handleiding](./GO2_HANDLEIDING.md)
- [Go2 SDK Repositories](./GO2_SDK_REPOSITORIES.md) - Officiële GitHub repositories
- [Unitree Developer Documentation](https://support.unitree.com/home/en/developer)
- [Project README](../README.md)

## Officiële SDK Repositories

- **unitree_sdk2**: https://github.com/unitreerobotics/unitree_sdk2 (C++ SDK)
- **unitree_sdk2_python**: https://github.com/unitreerobotics/unitree_sdk2_python (Python wrapper)
- **unitree_ros2**: https://github.com/unitreerobotics/unitree_ros2 (ROS2 pakket)
- **go2_description**: https://github.com/Unitree-Go2-Robot/go2_description (URDF bestanden)

Zie [GO2_SDK_REPOSITORIES.md](./GO2_SDK_REPOSITORIES.md) voor volledige details.

