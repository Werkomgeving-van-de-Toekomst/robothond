# RL Modellen op Fysieke Go2 Robot

Deze guide beschrijft hoe je getrainde RL modellen kunt laden en gebruiken op de fysieke Go2 robot.

## Overzicht

Na het trainen van RL modellen in simulatie, kun je deze modellen gebruiken om de fysieke Go2 robot te besturen. Het systeem ondersteunt:

- **Enkel model**: Laad één model en gebruik het
- **Meerdere modellen**: Laad meerdere modellen en wissel tussen hen
- **Model manager**: Beheer meerdere modellen tegelijk

## Installatie

Zorg dat je alle dependencies hebt:

```bash
conda activate pybullet  # Of je normale venv
pip install stable-baselines3 numpy
```

## Basis Gebruik

### Enkel Model

Run één getraind model op de robot:

```bash
python src/examples/run_rl_on_robot.py models/go2_rl/best_model/best_model.zip
```

Met opties:

```bash
python src/examples/run_rl_on_robot.py \
    models/go2_rl/best_model/best_model.zip \
    --max-steps 2000 \
    --frequency 20.0
```

### Meerdere Modellen

Laad meerdere modellen en wissel tussen hen:

```bash
python src/examples/run_rl_on_robot.py \
    --models walking:models/go2_rl/best_model/best_model.zip \
              stairs:models/go2_stairs/best_model/best_model.zip \
    --switch-after 500 \
    --frequency 20.0
```

Dit wisselt automatisch tussen de modellen elke 500 stappen.

## Python API

### Enkel Model Gebruiken

```python
from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.rl_controller import Go2RLController

# Connect met robot
robot = Go2Robot()
robot.connect()

try:
    # Laad RL model
    controller = Go2RLController(
        robot=robot,
        model_path="models/go2_rl/best_model/best_model.zip"
    )
    
    # Run episode
    controller.run_episode(max_steps=1000, frequency=20.0)
    
    # Of handmatig stappen
    for i in range(100):
        info = controller.step()
        print(f"Step {i}: {info}")
        time.sleep(0.05)  # 20 Hz
        
finally:
    robot.disconnect()
```

### Meerdere Modellen Beheren

```python
from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.rl_controller import Go2ModelManager

# Connect met robot
robot = Go2Robot()
robot.connect()

try:
    # Maak model manager
    manager = Go2ModelManager(robot)
    
    # Laad meerdere modellen
    manager.load_model(
        name="walking",
        model_path="models/go2_rl/best_model/best_model.zip"
    )
    
    manager.load_model(
        name="stairs",
        model_path="models/go2_stairs/best_model/best_model.zip"
    )
    
    # Wissel tussen modellen
    controller = manager.switch_model("walking")
    controller.run_episode(max_steps=500)
    
    controller = manager.switch_model("stairs")
    controller.run_episode(max_steps=500)
    
    # Lijst alle modellen
    print(f"Geladen modellen: {manager.list_models()}")
    
finally:
    robot.disconnect()
```

### Model uit Directory Laden

```python
# Laad automatisch best_model.zip uit directory
manager.load_from_directory(
    name="walking",
    model_dir="models/go2_rl"
)

# Of specificeer bestand
manager.load_from_directory(
    name="stairs",
    model_dir="models/go2_stairs",
    model_file="final_model.zip"
)
```

## Parameters

### Command Line

- `model_path`: Pad naar model bestand (voor enkel model)
- `--models`: Meerdere modellen in formaat `name:path`
- `--max-steps`: Maximum aantal stappen (default: 1000)
- `--frequency`: Control frequentie in Hz (default: 20.0)
- `--switch-after`: Aantal stappen voor wisselen (default: 500)

### Python API

#### Go2RLController

- `robot`: Go2Robot instantie
- `model_path`: Pad naar getraind model
- `observation_normalizer`: Normalisatie parameters (optioneel)

#### Go2ModelManager

- `robot`: Go2Robot instantie
- `models_dir`: Directory met modellen (optioneel)

## Belangrijke Aanpassingen

⚠️ **LET OP**: De huidige implementatie bevat placeholders voor de echte Go2 API. Je moet de volgende functies aanpassen aan de daadwerkelijke Go2 SDK:

### 1. Observation Ophalen

In `Go2RLController._get_observation()`:

```python
# Vervang placeholders met echte Go2 API calls
state = self.robot.get_state()
joint_positions = state.joint_positions  # Echte API call
base_pos = state.base_position  # Echte API call
# etc.
```

### 2. Joint Commando's Sturen

In `Go2RLController.step()`:

```python
# Vervang met echte Go2 API
self.robot.set_joint_positions(joint_targets)  # Echte API call
# Of:
self.robot.send_joint_command(joint_targets)  # Afhankelijk van API
```

### 3. Joint Namen

Controleer of de joint namen overeenkomen met de echte Go2:
- `FL_hip_joint`, `FL_thigh_joint`, `FL_calf_joint`
- `FR_hip_joint`, `FR_thigh_joint`, `FR_calf_joint`
- `RL_hip_joint`, `RL_thigh_joint`, `RL_calf_joint`
- `RR_hip_joint`, `RR_thigh_joint`, `RR_calf_joint`

### 4. Joint Limits

Pas joint limits aan aan echte Go2 specificaties in:
- `Go2RLController._scale_action_to_joints()`
- `Go2RLController._get_observation()` (voor traplopen model)

## Veiligheid

⚠️ **BELANGRIJK**: Test altijd eerst in simulatie voordat je op de fysieke robot gebruikt!

1. **Start met lage frequentie**: Begin met 10-20 Hz
2. **Monitor robot**: Houd robot altijd in de gaten
3. **Emergency stop**: Zorg dat je snel kunt stoppen
4. **Test eerst**: Test modellen eerst in simulatie
5. **Begin klein**: Start met korte episodes

## Troubleshooting

### Model laadt niet

- Check of model pad correct is
- Verifieer dat model type (PPO/SAC/TD3) correct is
- Check of Stable-Baselines3 geïnstalleerd is

### Robot beweegt niet

- Check robot verbinding
- Verifieer joint namen
- Check of joint commando's correct worden gestuurd
- Test eerst met simpele commando's

### Observaties komen niet overeen

- Check of observation dimensies overeenkomen
- Verifieer dat robot state correct wordt opgehaald
- Pas observation normalisatie aan indien nodig

## Voorbeelden

### Voorbeeld 1: Basis Gebruik

```bash
# Train model
python src/examples/train_rl.py --algorithm PPO --timesteps 100000

# Run op robot
python src/examples/run_rl_on_robot.py models/go2_rl/best_model/best_model.zip
```

### Voorbeeld 2: Meerdere Modellen

```bash
# Train verschillende modellen
python src/examples/train_rl.py --algorithm PPO --timesteps 100000 --save-path models/walking
python src/examples/train_stairs.py --algorithm PPO --timesteps 200000 --save-path models/stairs

# Run beide op robot
python src/examples/run_rl_on_robot.py \
    --models walking:models/walking/best_model/best_model.zip \
              stairs:models/stairs/best_model/best_model.zip \
    --switch-after 1000
```

### Voorbeeld 3: Python Script

```python
#!/usr/bin/env python3
from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.rl_controller import Go2ModelManager

robot = Go2Robot()
robot.connect()

try:
    manager = Go2ModelManager(robot)
    
    # Laad modellen
    manager.load_from_directory("walking", "models/go2_rl")
    manager.load_from_directory("stairs", "models/go2_stairs")
    
    # Wissel tussen modellen
    for i in range(5):
        model_name = "walking" if i % 2 == 0 else "stairs"
        controller = manager.switch_model(model_name)
        print(f"Gebruik model: {model_name}")
        controller.run_episode(max_steps=500, frequency=20.0)
        
finally:
    robot.disconnect()
```

## Volgende Stappen

1. **Pas API calls aan**: Integreer met echte Go2 SDK
2. **Test in simulatie**: Verifieer dat alles werkt
3. **Test op robot**: Begin met korte episodes
4. **Monitor performance**: Check of modellen goed werken
5. **Fine-tune**: Pas parameters aan indien nodig

