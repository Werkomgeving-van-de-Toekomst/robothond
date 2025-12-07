# Unitree Go2 EDU API Documentatie

## Go2Robot Klasse

### Initialisatie

```python
from src.unitree_go2 import Go2Robot

robot = Go2Robot(ip_address="192.168.123.161", port=8080, timeout=5.0)
```

### Methoden

#### `connect() -> bool`
Maak verbinding met de robot.

#### `disconnect()`
Verbreek verbinding met de robot.

#### `stand()`
Laat robot rechtop staan.

#### `sit()`
Laat robot zitten.

#### `move(vx: float, vy: float, vyaw: float)`
Beweeg robot met opgegeven snelheden.

- `vx`: Snelheid vooruit/achteruit (m/s)
- `vy`: Snelheid links/rechts (m/s)  
- `vyaw`: Draaisnelheid (rad/s)

#### `stop()`
Stop alle beweging.

#### `get_state() -> Dict[str, Any]`
Haal robot status op.

### Context Manager

```python
with Go2Robot(ip_address="192.168.123.161") as robot:
    robot.stand()
    robot.move(0.3, 0.0, 0.0)
```

## Exceptions

- `Go2ConnectionError`: Fout bij verbinden
- `Go2CommandError`: Fout bij commando
- `Go2TimeoutError`: Timeout bij communicatie

## Referenties

- [Unitree Developer Documentation](https://support.unitree.com/home/en/developer)

