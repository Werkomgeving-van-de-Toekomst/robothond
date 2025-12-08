#!/usr/bin/env python3
"""
Reinforcement Learning Training Script voor Traplopen met Go2 Robot

Train een RL agent om de Go2 robot traplopen te leren.
"""

import sys
import os
from pathlib import Path
import argparse
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.simulation.go2_stairs_env import Go2StairsEnv

try:
    from stable_baselines3 import PPO, SAC, TD3
    from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
    from stable_baselines3.common.vec_env import DummyVecEnv
except ImportError:
    print("ERROR: Stable-Baselines3 niet geïnstalleerd")
    print("Installeer met: conda activate pybullet && pip install stable-baselines3")
    sys.exit(1)


def make_env(gui=False, stair_config=None):
    """Maak traplopen environment"""
    def _init():
        env = Go2StairsEnv(gui=gui, stair_config=stair_config, max_episode_steps=2000)
        return env
    return _init


def train(
    algorithm: str = "PPO",
    total_timesteps: int = 200000,
    gui: bool = False,
    save_path: str = "models/go2_stairs",
    load_model: Optional[str] = None,
    num_steps: int = 5,
    step_height: float = 0.15,
    step_depth: float = 0.25,
    step_width: float = 0.5,
    start_distance: float = 1.0
):
    """Train RL agent voor traplopen"""
    
    stair_config = {
        "num_steps": num_steps,
        "step_height": step_height,
        "step_depth": step_depth,
        "step_width": step_width,
        "start_distance": start_distance
    }
    
    print("=" * 70)
    print(f"  RL Training - Traplopen - {algorithm}")
    print("=" * 70)
    print(f"\nTrap Configuratie:")
    print(f"  Aantal treden: {num_steps}")
    print(f"  Trede hoogte: {step_height}m")
    print(f"  Trede diepte: {step_depth}m")
    print(f"  Trap breedte: {step_width}m")
    print(f"  Start afstand: {start_distance}m")
    print(f"\nTraining Parameters:")
    print(f"  Algorithm: {algorithm}")
    print(f"  Total timesteps: {total_timesteps}")
    print(f"  GUI: {gui}")
    print(f"  Save path: {save_path}\n")
    
    # Maak environment
    print("✓ Environment aanmaken...")
    env = DummyVecEnv([make_env(gui=gui, stair_config=stair_config)])
    
    # Maak model
    print(f"✓ {algorithm} model aanmaken...")
    
    if load_model and os.path.exists(load_model):
        print(f"  Laden van bestaand model: {load_model}")
        if algorithm == "PPO":
            model = PPO.load(load_model, env=env)
        elif algorithm == "SAC":
            model = SAC.load(load_model, env=env)
        elif algorithm == "TD3":
            model = TD3.load(load_model, env=env)
        else:
            raise ValueError(f"Onbekend algoritme: {algorithm}")
    else:
        if algorithm == "PPO":
            model = PPO(
                "MlpPolicy",
                env,
                verbose=1,
                tensorboard_log=f"{save_path}/tensorboard",
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01,
            )
        elif algorithm == "SAC":
            model = SAC(
                "MlpPolicy",
                env,
                verbose=1,
                tensorboard_log=f"{save_path}/tensorboard",
                learning_rate=3e-4,
                buffer_size=100000,
                learning_starts=1000,
                batch_size=256,
                tau=0.005,
                gamma=0.99,
            )
        elif algorithm == "TD3":
            model = TD3(
                "MlpPolicy",
                env,
                verbose=1,
                tensorboard_log=f"{save_path}/tensorboard",
                learning_rate=3e-4,
                buffer_size=100000,
                learning_starts=1000,
                batch_size=256,
                tau=0.005,
                gamma=0.99,
            )
        else:
            raise ValueError(f"Onbekend algoritme: {algorithm}")
    
    # Maak save directory
    os.makedirs(save_path, exist_ok=True)
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path=f"{save_path}/checkpoints",
        name_prefix="go2_stairs"
    )
    
    eval_env = DummyVecEnv([make_env(gui=False, stair_config=stair_config)])
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=f"{save_path}/best_model",
        log_path=f"{save_path}/logs",
        eval_freq=5000,
        deterministic=True,
        render=False
    )
    
    # Train
    print("\n✓ Training starten...")
    print("  Druk Ctrl+C om te stoppen\n")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=True
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Training gestopt door gebruiker")
    
    # Sla final model op
    final_model_path = f"{save_path}/final_model"
    print(f"\n✓ Model opslaan naar {final_model_path}")
    model.save(final_model_path)
    
    # Sla trap configuratie op
    import json
    config_path = f"{save_path}/stair_config.json"
    with open(config_path, 'w') as f:
        json.dump(stair_config, f, indent=2)
    print(f"✓ Trap configuratie opgeslagen: {config_path}")
    
    # Sluit environments
    env.close()
    eval_env.close()
    
    print("\n✓ Training voltooid!")
    print(f"  Model opgeslagen: {final_model_path}")
    print(f"  Best model: {save_path}/best_model")
    print(f"  Tensorboard logs: {save_path}/tensorboard")
    print(f"\n  Bekijk training met: tensorboard --logdir {save_path}/tensorboard")


def main():
    parser = argparse.ArgumentParser(
        description="Train RL agent voor traplopen met Go2 robot"
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="PPO",
        choices=["PPO", "SAC", "TD3"],
        help="RL algoritme (default: PPO)"
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=200000,
        help="Aantal training timesteps (default: 200000)"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Toon PyBullet GUI tijdens training"
    )
    parser.add_argument(
        "--save-path",
        type=str,
        default="models/go2_stairs",
        help="Pad om model op te slaan (default: models/go2_stairs)"
    )
    parser.add_argument(
        "--load-model",
        type=str,
        default=None,
        help="Pad naar bestaand model om te laden (optioneel)"
    )
    parser.add_argument(
        "--num-steps",
        type=int,
        default=5,
        help="Aantal treden (default: 5)"
    )
    parser.add_argument(
        "--step-height",
        type=float,
        default=0.15,
        help="Hoogte per trede in meters (default: 0.15)"
    )
    parser.add_argument(
        "--step-depth",
        type=float,
        default=0.25,
        help="Diepte per trede in meters (default: 0.25)"
    )
    parser.add_argument(
        "--step-width",
        type=float,
        default=0.5,
        help="Breedte van trap in meters (default: 0.5)"
    )
    parser.add_argument(
        "--start-distance",
        type=float,
        default=1.0,
        help="Afstand van robot tot trap in meters (default: 1.0)"
    )
    
    args = parser.parse_args()
    
    train(
        algorithm=args.algorithm,
        total_timesteps=args.timesteps,
        gui=args.gui,
        save_path=args.save_path,
        load_model=args.load_model,
        num_steps=args.num_steps,
        step_height=args.step_height,
        step_depth=args.step_depth,
        step_width=args.step_width,
        start_distance=args.start_distance
    )


if __name__ == "__main__":
    main()

