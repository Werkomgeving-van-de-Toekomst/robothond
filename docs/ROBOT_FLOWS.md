# Robot Flows voor Go2

Flows zijn geautomatiseerde actiesequenties die de robot uitvoert. Je kunt flows gebruiken om complexe gedragingen te programmeren zoals "loop naar iemand, hurk, en heet welkom".

## Overzicht

Een flow bestaat uit een reeks acties die sequentieel worden uitgevoerd:
- Bewegingen (lopen, draaien, staan, zitten, hurken)
- Spraak (via voice controller)
- Wachten
- Conditionele acties
- Loops
- Parallelle acties

## Snel Starten

### Voorbeeld: Welcome Flow

```bash
python src/examples/run_flow.py --flow welcome --distance 2.0 --voice
```

Dit voert uit:
1. Robot staat op
2. Loopt 2 meter vooruit
3. Stopt
4. Hurkt
5. Zegt "Welkom! Leuk je te zien!"
6. Wacht 2 seconden
7. Staat weer op

## Flow Actie Types

### Stand
Laat robot rechtop staan.

```yaml
- name: "Sta op"
  type: stand
  duration: 2.0  # Tijd om te stabiliseren
```

### Sit
Laat robot zitten.

```yaml
- name: "Ga zitten"
  type: sit
  duration: 2.0
```

### Crouch
Laat robot hurken (tussen stand en sit).

```yaml
- name: "Hurk"
  type: crouch
  params:
    height: 0.4  # 0.0 = volledig zitten, 1.0 = volledig staan
  duration: 2.0
```

### Move
Beweeg robot met constante snelheid.

```yaml
- name: "Loop vooruit"
  type: move
  params:
    vx: 0.3      # Snelheid vooruit/achteruit (m/s)
    vy: 0.0      # Snelheid links/rechts (m/s)
    vyaw: 0.0    # Draaisnelheid (rad/s)
  duration: 3.0  # Duur in seconden
```

### Move To
Beweeg naar specifieke positie.

```yaml
- name: "Ga naar positie"
  type: move_to
  params:
    x: 2.0       # X positie (meter)
    y: 1.0       # Y positie (meter)
    yaw: 0.0     # Orientatie (rad, optioneel)
    speed: 0.3   # Bewegingssnelheid (m/s)
```

### Rotate
Draai robot over specifieke hoek.

```yaml
- name: "Draai 90 graden"
  type: rotate
  params:
    angle: 90    # Hoek in graden
    speed: 0.5  # Draaisnelheid (rad/s)
```

### Stop
Stop alle beweging.

```yaml
- name: "Stop"
  type: stop
  duration: 0.5
```

### Wait
Wacht voor bepaalde tijd.

```yaml
- name: "Wacht"
  type: wait
  duration: 2.0  # Seconden
```

### Speak / Voice Speak
Spreek tekst uit (via voice controller).

```yaml
- name: "Groet"
  type: voice_speak
  params:
    text: "Hallo! Ik ben de Go2 robot."
```

### Condition
Voer acties uit op basis van conditie.

```yaml
- name: "Conditionele actie"
  type: condition
  condition: "self.current_position[0] > 1.0"  # Python expressie
  params:
    actions:
      - type: voice_speak
        params:
          text: "Ik ben ver genoeg gelopen"
```

### Loop
Herhaal acties meerdere keren.

```yaml
- name: "Herhaal beweging"
  type: loop
  params:
    count: 3
    actions:
      - type: move
        params:
          vx: 0.3
        duration: 1.0
      - type: wait
        duration: 0.5
```

### Parallel
Voer meerdere acties parallel uit.

```yaml
- name: "Parallelle acties"
  type: parallel
  params:
    actions:
      - type: move
        params:
          vx: 0.3
        duration: 5.0
      - type: voice_speak
        params:
          text: "Ik loop nu"
```

## YAML Flow Bestanden

Maak een YAML bestand met je flow:

```yaml
name: "Mijn Flow"
description: "Beschrijving van wat de flow doet"

actions:
  - name: "Sta op"
    type: stand
    duration: 2.0
    
  - name: "Loop"
    type: move
    params:
      vx: 0.3
    duration: 3.0
    
  - name: "Stop"
    type: stop
```

Voer uit:
```bash
python src/examples/run_flow.py --yaml flows/mijn_flow.yaml
```

## Python API

### Basis Gebruik

```python
from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.flow_executor import FlowExecutor, create_welcome_flow
from src.voice.voice_controller import Go2VoiceController

# Connect robot
robot = Go2Robot(ip_address="192.168.123.161")
robot.connect()

# Setup voice (optioneel)
voice_controller = Go2VoiceController(robot=robot)

# Maak executor
executor = FlowExecutor(robot, voice_controller)

# Gebruik voorgebouwde flow
actions = create_welcome_flow(distance=2.0)
executor.execute_flow(actions)

# Of maak custom flow
custom_actions = [
    {
        "name": "Sta op",
        "type": "stand",
        "duration": 2.0
    },
    {
        "name": "Loop",
        "type": "move",
        "params": {"vx": 0.3, "vy": 0.0, "vyaw": 0.0},
        "duration": 3.0
    },
    {
        "name": "Groet",
        "type": "voice_speak",
        "params": {"text": "Hallo!"}
    }
]

executor.execute_flow(custom_actions)
```

### Callbacks

```python
def on_action_start(name):
    print(f"Start: {name}")

def on_action_end(name):
    print(f"Klaar: {name}")

def on_flow_complete():
    print("Flow voltooid!")

executor.on_action_start = on_action_start
executor.on_action_end = on_action_end
executor.on_flow_complete = on_flow_complete
```

### Flow Stoppen

```python
# In andere thread
executor.stop()
```

## Voorbeelden

### Voorbeeld 1: Welcome Flow

```bash
python src/examples/run_flow.py --flow welcome --distance 2.0 --voice
```

### Voorbeeld 2: Custom YAML Flow

```bash
python src/examples/run_flow.py --yaml flows/custom_flow_example.yaml --voice
```

### Voorbeeld 3: Python Script

```python
from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.flow_executor import FlowExecutor

robot = Go2Robot()
robot.connect()

executor = FlowExecutor(robot)

# Maak flow
actions = [
    {"type": "stand", "duration": 2.0},
    {"type": "move", "params": {"vx": 0.3}, "duration": 5.0},
    {"type": "stop"},
    {"type": "crouch", "params": {"height": 0.4}, "duration": 2.0},
    {"type": "stand", "duration": 2.0}
]

executor.execute_flow(actions)
robot.disconnect()
```

## Geavanceerd Gebruik

### Conditionele Acties

```yaml
- type: condition
  condition: "distance_to_target < 1.0"
  params:
    actions:
      - type: stop
      - type: voice_speak
        params:
          text: "Ik ben aangekomen"
```

### Loops

```yaml
- type: loop
  params:
    count: 5
    actions:
      - type: move
        params:
          vx: 0.2
        duration: 1.0
      - type: rotate
        params:
          angle: 72  # 360 / 5 = 72 graden per stap
```

### Parallelle Acties

```yaml
- type: parallel
  params:
    actions:
      - type: move
        params:
          vx: 0.3
        duration: 10.0
      - type: loop
        params:
          count: 5
          actions:
            - type: voice_speak
              params:
                text: "Ik loop nog steeds"
            - type: wait
              duration: 2.0
```

## Best Practices

1. **Test eerst**: Test flows eerst zonder robot of met kleine bewegingen
2. **Veiligheid**: Zorg voor voldoende ruimte en emergency stop
3. **Timing**: Geef robot tijd om te stabiliseren tussen acties
4. **Voice**: Gebruik `--voice` flag voor spraak acties
5. **Fouten**: Gebruik `stop_on_error=False` om door te gaan bij fouten

## Troubleshooting

### Flow stopt niet

```python
executor.stop()  # Forceer stop
robot.stop()      # Stop robot beweging
```

### Voice werkt niet

- Zorg dat `--voice` flag gebruikt wordt
- Check of voice dependencies geïnstalleerd zijn
- Test voice controller apart

### Beweging niet nauwkeurig

- `move_to` gebruikt simpele schattingen
- Voor nauwkeurige positionering gebruik odometry of visuele feedback
- Test bewegingen eerst met kleine afstanden

## Volgende Stappen

1. **Maak je eigen flows**: Gebruik YAML of Python
2. **Integreer met voice**: Gebruik voice commando's om flows te starten
3. **Voeg sensoren toe**: Gebruik robot state voor conditionele acties
4. **Maak complexe gedragingen**: Combineer loops, conditions, en parallelle acties

