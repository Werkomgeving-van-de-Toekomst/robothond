# Reinforcement Learning voor Unitree Go2

Deze guide beschrijft hoe je Reinforcement Learning (RL) kunt gebruiken om de Go2 robot te trainen.

## Overzicht

De RL setup gebruikt:
- **Gymnasium**: Standaard RL environment interface
- **Stable-Baselines3**: State-of-the-art RL algoritmes (PPO, SAC, TD3)
- **PyBullet**: Physics simulatie voor training

## Installatie

### Stap 1: Activeer conda environment

```bash
conda activate pybullet
```

### Stap 2: Installeer RL dependencies

```bash
pip install stable-baselines3 gymnasium tensorboard
```

Of gebruik het requirements bestand:

```bash
pip install -r requirements_rl.txt
```

## Environment

Het RL environment (`Go2RLEnv`) heeft:

### Observation Space (37 dimensies)
- 12 joint posities
- 12 joint snelheden
- 3 base positie (x, y, z)
- 4 base orientatie (quaternion)
- 3 base lineaire snelheid
- 3 base hoeksnelheid

### Action Space (12 dimensies)
- 12 joint target posities (genormaliseerd naar [-1, 1])
- Wordt automatisch geschaald naar joint limits

### Reward Functies

#### Walking Reward
- **+10.0** per unit voorwaartse snelheid
- **-5.0** per unit zijwaartse snelheid (stabiliteit)
- **-2.0** per unit rotatie (stabiliteit)
- **-10.0** per meter hoogte afwijking
- **+1.0** voor lage joint snelheden (stabiliteit)
- **-5.0** voor extreme joint posities
- **+0.1** survival bonus

#### Standing Reward
- **+10.0** voor stabiele hoogte
- **-5.0** voor beweging
- **-2.0** voor rotatie
- **+0.1** survival bonus

## Training

### Basis Training

Train een PPO agent voor 100k timesteps:

```bash
conda activate pybullet
python src/examples/train_rl.py --algorithm PPO --timesteps 100000
```

### Met GUI (langzamer, maar visueel)

```bash
python src/examples/train_rl.py --algorithm PPO --timesteps 100000 --gui
```

### Verschillende Algoritmes

#### PPO (Aanbevolen voor beginners)
```bash
python src/examples/train_rl.py --algorithm PPO --timesteps 100000
```

#### SAC (Goed voor continuous control)
```bash
python src/examples/train_rl.py --algorithm SAC --timesteps 100000
```

#### TD3 (Alternatief voor continuous control)
```bash
python src/examples/train_rl.py --algorithm TD3 --timesteps 100000
```

### Training Parameters

- `--algorithm`: RL algoritme (PPO, SAC, TD3)
- `--timesteps`: Aantal training timesteps
- `--gui`: Toon PyBullet GUI tijdens training
- `--reward`: Reward type (walking, standing)
- `--save-path`: Pad om model op te slaan
- `--load-model`: Laad bestaand model om verder te trainen

### Voorbeeld: Lange Training

```bash
# Train voor 1 miljoen timesteps
python src/examples/train_rl.py \
    --algorithm PPO \
    --timesteps 1000000 \
    --save-path models/go2_rl_long
```

### Training Monitoring

Tijdens training worden automatisch opgeslagen:
- **Checkpoints**: Elke 10k timesteps in `models/go2_rl/checkpoints/`
- **Best model**: Beste model tijdens evaluatie in `models/go2_rl/best_model/`
- **Tensorboard logs**: In `models/go2_rl/tensorboard/`

Bekijk training progress:

```bash
tensorboard --logdir models/go2_rl/tensorboard
```

## Evaluatie

### Evalueer Getraind Model

```bash
python src/examples/evaluate_rl.py models/go2_rl/best_model/best_model.zip --episodes 10
```

### Zonder GUI (sneller)

```bash
python src/examples/evaluate_rl.py models/go2_rl/best_model/best_model.zip --episodes 10 --no-gui
```

## Custom Reward Functie

Je kunt een custom reward functie maken door `Go2RLEnv` te subclassen:

```python
from src.simulation.go2_rl_env import Go2RLEnv

class CustomGo2Env(Go2RLEnv):
    def _calculate_reward(self):
        # Je custom reward logica hier
        reward = 0.0
        # ...
        return reward
```

## Tips voor Training

1. **Start met korte episodes**: Gebruik `max_episode_steps=500` voor snellere iteratie
2. **Gebruik geen GUI tijdens training**: GUI vertraagt training significant
3. **Monitor met Tensorboard**: Check training progress regelmatig
4. **Experimenteer met reward functies**: Verschillende rewards leiden tot verschillende gedrag
5. **Gebruik checkpoints**: Sla regelmatig op zodat je niet alles opnieuw hoeft te trainen

## Troubleshooting

### Out of Memory

- Verlaag `batch_size` in training script
- Gebruik minder parallelle environments
- Train met kortere episodes

### Training convergeert niet

- Probeer verschillende reward functies
- Experimenteer met learning rate
- Check of observation space correct is

### Model leert niet

- Verifieer dat reward functie correct werkt
- Check of action space correct geschaald wordt
- Zorg dat environment correct reset

## Voorbeelden

### Voorbeeld 1: Basis Training

```bash
# Train PPO agent
conda activate pybullet
python src/examples/train_rl.py --algorithm PPO --timesteps 100000

# Evalueer
python src/examples/evaluate_rl.py models/go2_rl/best_model/best_model.zip
```

### Voorbeeld 2: Verder Trainen

```bash
# Laad bestaand model en train verder
python src/examples/train_rl.py \
    --algorithm PPO \
    --timesteps 200000 \
    --load-model models/go2_rl/checkpoints/go2_rl_100000_steps.zip
```

### Voorbeeld 3: Standing Task

```bash
# Train voor standing task
python src/examples/train_rl.py \
    --algorithm PPO \
    --timesteps 100000 \
    --reward standing \
    --save-path models/go2_standing
```

## Referenties

- [Stable-Baselines3 Documentation](https://stable-baselines3.readthedocs.io/)
- [Gymnasium Documentation](https://gymnasium.farama.org/)
- [PyBullet Documentation](https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/)

