"""
Reinforcement Learning Environment voor Unitree Go2

Gymnasium-compatible environment voor RL training van de Go2 robot.
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, Tuple, Optional, Any
import pybullet as p

from .go2_simulator import Go2Simulator


class Go2RLEnv(gym.Env):
    """
    Reinforcement Learning Environment voor Go2 robot
    
    Observation Space:
    - Joint positions (12 joints)
    - Joint velocities (12 joints)
    - Base position (x, y, z)
    - Base orientation (quaternion x, y, z, w)
    - Base linear velocity (x, y, z)
    - Base angular velocity (x, y, z)
    Total: 12 + 12 + 3 + 4 + 3 + 3 = 37 dimensions
    
    Action Space:
    - Joint target positions (12 joints)
    Range: [-1, 1] wordt geschaald naar joint limits
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(
        self,
        render_mode: Optional[str] = None,
        gui: bool = True,
        max_episode_steps: int = 1000,
        reward_type: str = "walking"
    ):
        """
        Initialiseer RL environment
        
        Args:
            render_mode: Rendering mode ("human" of "rgb_array")
            gui: Toon PyBullet GUI
            max_episode_steps: Maximum aantal stappen per episode
            reward_type: Type reward functie ("walking", "standing", "custom")
        """
        super().__init__()
        
        self.render_mode = render_mode
        self.gui = gui or (render_mode == "human")
        self.max_episode_steps = max_episode_steps
        self.reward_type = reward_type
        
        # Simulator
        self.sim = None
        
        # Episode tracking
        self.step_count = 0
        self.episode_reward = 0.0
        
        # Define observation space
        # 12 joint positions + 12 joint velocities + 3 base pos + 4 base ori + 3 base lin vel + 3 base ang vel
        obs_dim = 12 + 12 + 3 + 4 + 3 + 3
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32
        )
        
        # Define action space (12 joints, normalized to [-1, 1])
        self.action_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(12,),
            dtype=np.float32
        )
        
        # Joint limits voor scaling van actions
        # Hip: ±0.5 rad, Thigh: 0.0-1.0 rad, Calf: -1.5-0.0 rad
        self.joint_limits = np.array([
            [-0.5, 0.5],   # Hip joints (4x)
            [-0.5, 0.5],
            [-0.5, 0.5],
            [-0.5, 0.5],
            [0.0, 1.0],    # Thigh joints (4x)
            [0.0, 1.0],
            [0.0, 1.0],
            [0.0, 1.0],
            [-1.5, 0.0],   # Calf joints (4x)
            [-1.5, 0.0],
            [-1.5, 0.0],
            [-1.5, 0.0],
        ])
        
    def _get_obs(self) -> np.ndarray:
        """Haal observation op"""
        if self.sim is None:
            return np.zeros(self.observation_space.shape, dtype=np.float32)
        
        # Joint states
        joint_states = self.sim.get_joint_states()
        joint_positions = []
        joint_velocities = []
        
        for joint_name in self.sim.joint_names:
            state = joint_states[joint_name]
            joint_positions.append(state['position'])
            joint_velocities.append(state['velocity'])
        
        joint_positions = np.array(joint_positions, dtype=np.float32)
        joint_velocities = np.array(joint_velocities, dtype=np.float32)
        
        # Base pose
        base_pos, base_ori = self.sim.get_base_pose()
        base_lin_vel, base_ang_vel = self.sim.get_base_velocity()
        
        # Combineer alle observaties
        obs = np.concatenate([
            joint_positions,
            joint_velocities,
            np.array(base_pos, dtype=np.float32),
            np.array(base_ori, dtype=np.float32),
            np.array(base_lin_vel, dtype=np.float32),
            np.array(base_ang_vel, dtype=np.float32),
        ])
        
        return obs
    
    def _get_info(self) -> Dict[str, Any]:
        """Haal extra info op"""
        return {
            "step_count": self.step_count,
            "episode_reward": self.episode_reward,
        }
    
    def _calculate_reward(self) -> float:
        """Bereken reward"""
        if self.sim is None:
            return 0.0
        
        base_pos, base_ori = self.sim.get_base_pose()
        base_lin_vel, base_ang_vel = self.sim.get_base_velocity()
        joint_states = self.sim.get_joint_states()
        
        reward = 0.0
        
        if self.reward_type == "walking":
            # Reward voor voorwaartse beweging
            forward_velocity = base_lin_vel[0]  # x-richting
            reward += 10.0 * forward_velocity
            
            # Penalty voor zijwaartse beweging (stabiliteit)
            lateral_velocity = abs(base_lin_vel[1])
            reward -= 5.0 * lateral_velocity
            
            # Penalty voor rotatie (stabiliteit)
            angular_velocity_magnitude = np.linalg.norm(base_ang_vel)
            reward -= 2.0 * angular_velocity_magnitude
            
            # Penalty voor te veel hoogte variatie
            height_error = abs(base_pos[2] - 0.5)  # Target hoogte ~0.5m
            reward -= 10.0 * height_error
            
            # Reward voor stabiliteit (lage joint velocities)
            joint_velocities = [joint_states[name]['velocity'] for name in self.sim.joint_names]
            avg_joint_velocity = np.mean(np.abs(joint_velocities))
            reward += 1.0 * (1.0 - min(avg_joint_velocity, 1.0))
            
            # Penalty voor extreme joint posities
            joint_positions = [joint_states[name]['position'] for name in self.sim.joint_names]
            for i, pos in enumerate(joint_positions):
                if pos < self.joint_limits[i][0] or pos > self.joint_limits[i][1]:
                    reward -= 5.0
        
        elif self.reward_type == "standing":
            # Reward voor stabiel staan
            height_error = abs(base_pos[2] - 0.5)
            reward += 10.0 * (1.0 - min(height_error * 2, 1.0))
            
            # Penalty voor beweging
            velocity_magnitude = np.linalg.norm(base_lin_vel)
            reward -= 5.0 * velocity_magnitude
            
            # Penalty voor rotatie
            angular_velocity_magnitude = np.linalg.norm(base_ang_vel)
            reward -= 2.0 * angular_velocity_magnitude
        
        # Survival bonus
        reward += 0.1
        
        return reward
    
    def _is_done(self) -> bool:
        """Check of episode klaar is"""
        if self.sim is None:
            return True
        
        # Episode eindigt na max steps
        if self.step_count >= self.max_episode_steps:
            return True
        
        # Episode eindigt als robot valt
        base_pos, _ = self.sim.get_base_pose()
        if base_pos[2] < 0.2:  # Te laag = gevallen
            return True
        
        return False
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset environment"""
        super().reset(seed=seed)
        
        # Sluit oude simulator
        if self.sim is not None:
            self.sim.close()
        
        # Start nieuwe simulator
        self.sim = Go2Simulator(gui=self.gui)
        
        # Reset tracking
        self.step_count = 0
        self.episode_reward = 0.0
        
        # Reset robot naar start positie
        self.sim.reset()
        
        # Wacht even voor stabilisatie
        for _ in range(10):
            self.sim.step()
        
        obs = self._get_obs()
        info = self._get_info()
        
        return obs, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Voer actie uit"""
        if self.sim is None:
            raise RuntimeError("Environment niet geïnitialiseerd. Roep reset() aan eerst.")
        
        # Scale actions van [-1, 1] naar joint limits
        scaled_actions = np.zeros_like(action)
        for i in range(len(action)):
            low, high = self.joint_limits[i]
            scaled_actions[i] = low + (action[i] + 1.0) / 2.0 * (high - low)
        
        # Stel joint targets in
        targets = {}
        for i, joint_name in enumerate(self.sim.joint_names):
            targets[joint_name] = scaled_actions[i]
        
        self.sim.set_joint_targets(targets)
        
        # Simuleer stap
        self.sim.step()
        
        # Update tracking
        self.step_count += 1
        reward = self._calculate_reward()
        self.episode_reward += reward
        
        # Check done
        done = self._is_done()
        truncated = False  # Gymnasium gebruikt truncated voor time limits
        
        obs = self._get_obs()
        info = self._get_info()
        
        return obs, reward, done, truncated, info
    
    def render(self):
        """Render environment"""
        if self.render_mode == "human":
            # PyBullet GUI wordt automatisch getoond als gui=True
            pass
        elif self.render_mode == "rgb_array":
            # TODO: Implementeer RGB array rendering
            raise NotImplementedError("RGB array rendering nog niet geïmplementeerd")
    
    def close(self):
        """Sluit environment"""
        if self.sim is not None:
            self.sim.close()
            self.sim = None

