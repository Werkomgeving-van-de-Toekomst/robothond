#!/usr/bin/env python3
"""
Evaluateer getrainde RL agent voor traplopen
"""

import sys
import os
import json
from pathlib import Path
import argparse
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.simulation.go2_stairs_env import Go2StairsEnv

try:
    from stable_baselines3 import PPO, SAC, TD3
except ImportError:
    print("ERROR: Stable-Baselines3 niet geïnstalleerd")
    print("Installeer met: conda activate pybullet && pip install stable-baselines3")
    sys.exit(1)


def evaluate(
    model_path: str,
    num_episodes: int = 10,
    gui: bool = True,
    stair_config: dict = None
):
    """Evaluateer getrainde model voor traplopen"""
    
    print("=" * 70)
    print("  RL Model Evaluatie - Traplopen")
    print("=" * 70)
    print(f"\nModel: {model_path}")
    print(f"Episodes: {num_episodes}")
    print(f"GUI: {gui}")
    
    # Laad trap configuratie als beschikbaar
    config_path = os.path.join(os.path.dirname(model_path), "..", "stair_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        if stair_config is None:
            stair_config = loaded_config
        print(f"\nTrap Configuratie:")
        print(f"  Aantal treden: {stair_config.get('num_steps', 'N/A')}")
        step_h = stair_config.get('step_height', None)
        step_d = stair_config.get('step_depth', None)
        if step_h is not None:
            print(f"  Trede hoogte: {step_h*100:.1f}cm ({step_h}m)")
        if step_d is not None:
            print(f"  Trede diepte: {step_d*100:.1f}cm ({step_d}m)")
    elif stair_config is None:
        stair_config = {}
    
    print()
    
    # Laad model
    print("✓ Model laden...")
    if "PPO" in model_path or model_path.endswith("ppo"):
        model = PPO.load(model_path)
    elif "SAC" in model_path or model_path.endswith("sac"):
        model = SAC.load(model_path)
    elif "TD3" in model_path or model_path.endswith("td3"):
        model = TD3.load(model_path)
    else:
        # Probeer automatisch te detecteren
        try:
            model = PPO.load(model_path)
        except:
            try:
                model = SAC.load(model_path)
            except:
                model = TD3.load(model_path)
    
    # Maak environment
    print("✓ Environment aanmaken...")
    env = Go2StairsEnv(gui=gui, stair_config=stair_config, max_episode_steps=2000)
    
    # Run episodes
    print("\n✓ Episodes uitvoeren...\n")
    
    episode_rewards = []
    episode_lengths = []
    success_count = 0
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        done = False
        episode_reward = 0.0
        episode_length = 0
        
        print(f"Episode {episode + 1}/{num_episodes}...", end=" ", flush=True)
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        
        # Check of robot de top heeft bereikt
        if info.get("current_step_index", 0) >= info.get("num_steps", 0):
            success_count += 1
            print(f"✓ SUCCESS - Reward: {episode_reward:.2f}, Lengte: {episode_length}")
        else:
            print(f"✗ FAILED - Reward: {episode_reward:.2f}, Lengte: {episode_length}")
    
    # Statistieken
    print("\n" + "=" * 70)
    print("  Evaluatie Resultaten")
    print("=" * 70)
    print(f"\nSuccess rate: {success_count}/{num_episodes} ({100*success_count/num_episodes:.1f}%)")
    print(f"Gemiddelde reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"Gemiddelde lengte: {np.mean(episode_lengths):.2f} ± {np.std(episode_lengths):.2f}")
    print(f"Min reward: {np.min(episode_rewards):.2f}")
    print(f"Max reward: {np.max(episode_rewards):.2f}")
    
    env.close()


def main():
    parser = argparse.ArgumentParser(
        description="Evaluateer getrainde RL agent voor traplopen"
    )
    parser.add_argument(
        "model_path",
        type=str,
        help="Pad naar getraind model"
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=10,
        help="Aantal episodes (default: 10)"
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Geen GUI tonen"
    )
    parser.add_argument(
        "--num-steps",
        type=int,
        default=None,
        help="Aantal treden (override config)"
    )
    parser.add_argument(
        "--step-height",
        type=float,
        default=None,
        help="Hoogte per trede in centimeters (override config)"
    )
    parser.add_argument(
        "--step-depth",
        type=float,
        default=None,
        help="Diepte per trede in centimeters (override config)"
    )
    
    args = parser.parse_args()
    
    stair_config = {}
    if args.num_steps is not None:
        stair_config["num_steps"] = args.num_steps
    if args.step_height is not None:
        stair_config["step_height"] = args.step_height / 100.0  # cm naar m
    if args.step_depth is not None:
        stair_config["step_depth"] = args.step_depth / 100.0  # cm naar m
    
    evaluate(
        model_path=args.model_path,
        num_episodes=args.episodes,
        gui=not args.no_gui,
        stair_config=stair_config if stair_config else None
    )


if __name__ == "__main__":
    main()

