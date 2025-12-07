# PyBullet Simulatie Documentatie

PyBullet simulatie voor de Unitree Go2 EDU robot.

## Installatie

Installeer PyBullet:

```bash
pip install pybullet
```

Of installeer alle dependencies:

```bash
pip install -r requirements.txt
```

## Basis Gebruik

### Eenvoudige Simulatie

```python
from src.simulation import Go2Simulator

# Start simulator met GUI
with Go2Simulator() as sim:
    # Simuleer 10 seconden
    sim.run_simulation(10.0)
```

### Headless Simulatie (zonder GUI)

```python
# Start simulator zonder GUI (sneller voor batch processing)
with Go2Simulator(gui=False) as sim:
    sim.run_simulation(10.0)
```

## Voorbeelden

### Basis Simulatie

```bash
python src/examples/pybullet_simulation.py basic
```

### Beweging Simulatie

```bash
python src/examples/pybullet_simulation.py movement
```

### Sensor Data Simulatie

```bash
python src/examples/pybullet_simulation.py sensor
```

## API Referentie

### Go2Simulator Klasse

#### Initialisatie

```python
sim = Go2Simulator(
    urdf_path=None,      # Pad naar URDF (None = default)
    gui=True,            # Toon GUI
    gravity=-9.81,        # Zwaartekracht
    timestep=1.0/240.0    # Simulatie tijdstap
)
```

#### Methoden

##### Robot Control

- `reset(position, orientation)`: Reset robot naar beginpositie
- `set_joint_positions(positions)`: Stel joint posities direct in
- `set_joint_targets(targets, forces)`: Stel joint targets in voor position control

##### Sensor Data

- `get_joint_states()`: Haal alle joint states op (positie, snelheid, kracht)
- `get_base_pose()`: Haal base positie en orientatie op
- `get_base_velocity()`: Haal base snelheid op

##### Simulatie Control

- `step(steps=1)`: Voer simulatie stappen uit
- `run_simulation(duration, callback)`: Voer simulatie uit voor bepaalde duur
- `close()`: Sluit simulator

##### Debug

- `add_debug_line(start, end, color)`: Teken debug lijn

## Voorbeelden

### Joint Control

```python
from src.simulation import Go2Simulator

with Go2Simulator() as sim:
    # Haal joint namen op
    joint_states = sim.get_joint_states()
    joint_names = list(joint_states.keys())
    
    # Beweeg specifieke joint
    sim.set_joint_targets({
        'FL_hip_joint': 0.5,      # Front Left hip
        'FL_thigh_joint': 0.4,    # Front Left thigh
        'FL_calf_joint': -0.8     # Front Left calf
    })
    
    # Simuleer
    sim.run_simulation(5.0)
```

### Sensor Data Lezen

```python
from src.simulation import Go2Simulator

with Go2Simulator() as sim:
    for step in range(100):
        # Haal joint states op
        joints = sim.get_joint_states()
        
        # Haal base pose op
        position, orientation = sim.get_base_pose()
        linear_vel, angular_vel = sim.get_base_velocity()
        
        print(f"Positie: {position}")
        print(f"Snelheid: {linear_vel}")
        
        sim.step()
```

### Custom Callback

```python
from src.simulation import Go2Simulator

def my_callback(step, simulator):
    """Callback functie die elke stap wordt aangeroepen"""
    if step % 100 == 0:
        position, _ = simulator.get_base_pose()
        print(f"Step {step}: Positie = {position}")

with Go2Simulator() as sim:
    sim.run_simulation(10.0, callback=my_callback)
```

## Joint Namen

De Go2 heeft 12 actuated joints (3 per been):

- **FL_hip_joint**: Front Left hip
- **FL_thigh_joint**: Front Left thigh  
- **FL_calf_joint**: Front Left calf
- **FR_hip_joint**: Front Right hip
- **FR_thigh_joint**: Front Right thigh
- **FR_calf_joint**: Front Right calf
- **RL_hip_joint**: Rear Left hip
- **RL_thigh_joint**: Rear Left thigh
- **RL_calf_joint**: Rear Left calf
- **RR_hip_joint**: Rear Right hip
- **RR_thigh_joint**: Rear Right thigh
- **RR_calf_joint**: Rear Right calf

## Tips

1. **Performance**: Gebruik `gui=False` voor snellere simulatie zonder visualisatie
2. **Timestep**: Kleinere timestep = nauwkeuriger maar langzamer
3. **Joint Limits**: Respecteer joint limits om realistische beweging te krijgen
4. **Gravity**: Standaard -9.81 m/s², pas aan voor andere omgevingen

## Troubleshooting

### URDF niet gevonden

Zorg dat de URDF bestanden in `urdf/urdf/go2_description.urdf` staan.

### Mesh bestanden niet gevonden

De URDF verwijst naar mesh bestanden in `urdf/meshes/`. Zorg dat deze bestanden aanwezig zijn.

### Simulatie te langzaam

- Gebruik `gui=False` voor headless mode
- Verhoog `timestep` (maar let op: minder nauwkeurig)
- Reduceer aantal simulatie stappen

## Integratie met Echte Robot

Je kunt de simulator gebruiken om code te testen voordat je het op de echte robot uitvoert:

```python
from src.simulation import Go2Simulator
from src.unitree_go2 import Go2Robot

# Test eerst in simulatie
with Go2Simulator() as sim:
    # Test je code hier
    pass

# Dan op echte robot
with Go2Robot() as robot:
    # Zelfde code hier
    pass
```

