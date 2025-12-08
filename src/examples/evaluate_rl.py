#!/usr/bin/env python3
"""
Evaluateer getrainde RL agent voor Go2 Robot
"""

import sys
import os
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.simulation.go2_rl_env import Go2RLEnv

try:
    from stable_baselines3 import PPO, SAC, TD3
except ImportError:
    print("ERROR: Stable-Baselines3 niet geïnstalleerd")
    print("Installeer met: conda activate pybullet && pip install stable-baselines3")
    sys.exit(1)


def evaluate(model_path: str, num_episodes: int = 10, gui: bool = True, reward_type: str = "walking"):
    """Evaluateer getrainde model"""
    
    print("=" * 70)
    print("  RL Model Evaluatie")
    print("=" * 70)
    print(f"\nModel: {model_path}")
    print(f"Episodes: {num_episodes}")
    print(f"GUI: {gui}\n")
    
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
    env = Go2RLEnv(gui=gui, reward_type=reward_type, max_episode_steps=1000)
    
    # Run episodes
    print("\n✓ Episodes uitvoeren...\n")
    
    episode_rewards = []
    episode_lengths = []
    
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
        
        print(f"Reward: {episode_reward:.2f}, Lengte: {episode_length}")
    
    # Statistieken
    print("\n" + "=" * 70)
    print("  Evaluatie Resultaten")
    print("=" * 70)
    print(f"\nGemiddelde reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"Gemiddelde lengte: {np.mean(episode_lengths):.2f} ± {np.std(episode_lengths):.2f}")
    print(f"Min reward: {np.min(episode_rewards):.2f}")
    print(f"Max reward: {np.max(episode_rewards):.2f}")
    
    env.close()


def main():
    parser = argparse.ArgumentParser(
        description="Evaluateer getrainde RL agent"
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
        "--reward",
        type=str,
        default="walking",
        choices=["walking", "standing"],
        help="Reward type (default: walking)"
    )
    
    args = parser.parse_args()
    
    evaluate(
        model_path=args.model_path,
        num_episodes=args.episodes,
        gui=not args.no_gui,
        reward_type=args.reward
    )


if __name__ == "__main__":
    main()

