#!/usr/bin/env python3
"""
Reinforcement Learning Training Script voor Go2 Robot

Train een RL agent om de Go2 robot te laten lopen.
"""

import sys
import os
from pathlib import Path
import argparse
from typing import Optional

# Voeg project root toe aan path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.simulation.go2_rl_env import Go2RLEnv

try:
    from stable_baselines3 import PPO, SAC, TD3
    from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
    from stable_baselines3.common.monitor import Monitor
    from stable_baselines3.common.vec_env import DummyVecEnv
except ImportError:
    print("ERROR: Stable-Baselines3 niet geïnstalleerd")
    print("Installeer met: conda activate pybullet && pip install stable-baselines3")
    sys.exit(1)


def make_env(gui=False, reward_type="walking"):
    """Maak environment"""
    def _init():
        env = Go2RLEnv(gui=gui, reward_type=reward_type, max_episode_steps=1000)
        return env
    return _init


def train(
    algorithm: str = "PPO",
    total_timesteps: int = 100000,
    gui: bool = False,
    reward_type: str = "walking",
    save_path: str = "models/go2_rl",
    load_model: Optional[str] = None
):
    """Train RL agent"""
    
    print("=" * 70)
    print(f"  RL Training - {algorithm}")
    print("=" * 70)
    print(f"\nParameters:")
    print(f"  Algorithm: {algorithm}")
    print(f"  Total timesteps: {total_timesteps}")
    print(f"  GUI: {gui}")
    print(f"  Reward type: {reward_type}")
    print(f"  Save path: {save_path}\n")
    
    # Maak environment
    print("✓ Environment aanmaken...")
    env = DummyVecEnv([make_env(gui=gui, reward_type=reward_type)])
    
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
        name_prefix="go2_rl"
    )
    
    eval_env = DummyVecEnv([make_env(gui=False, reward_type=reward_type)])
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
        description="Train RL agent voor Go2 robot"
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
        default=100000,
        help="Aantal training timesteps (default: 100000)"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Toon PyBullet GUI tijdens training"
    )
    parser.add_argument(
        "--reward",
        type=str,
        default="walking",
        choices=["walking", "standing"],
        help="Reward type (default: walking)"
    )
    parser.add_argument(
        "--save-path",
        type=str,
        default="models/go2_rl",
        help="Pad om model op te slaan (default: models/go2_rl)"
    )
    parser.add_argument(
        "--load-model",
        type=str,
        default=None,
        help="Pad naar bestaand model om te laden (optioneel)"
    )
    
    args = parser.parse_args()
    
    train(
        algorithm=args.algorithm,
        total_timesteps=args.timesteps,
        gui=args.gui,
        reward_type=args.reward,
        save_path=args.save_path,
        load_model=args.load_model
    )


if __name__ == "__main__":
    main()

