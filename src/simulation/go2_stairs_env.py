"""
Reinforcement Learning Environment voor Traplopen met Go2

Gymnasium-compatible environment voor RL training van traplopen.
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, Tuple, Optional, Any, List
import pybullet as p

from .go2_simulator import Go2Simulator


class Go2StairsEnv(gym.Env):
    """
    Reinforcement Learning Environment voor traplopen met Go2 robot
    
    Observation Space:
    - Joint positions (12 joints)
    - Joint velocities (12 joints)
    - Base position (x, y, z)
    - Base orientation (quaternion x, y, z, w)
    - Base linear velocity (x, y, z)
    - Base angular velocity (x, y, z)
    - Next step position (x, y, z) - positie van volgende trede
    - Distance to next step (1)
    Total: 12 + 12 + 3 + 4 + 3 + 3 + 3 + 1 = 41 dimensions
    
    Action Space:
    - Joint target positions (12 joints)
    Range: [-1, 1] wordt geschaald naar joint limits
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(
        self,
        render_mode: Optional[str] = None,
        gui: bool = True,
        max_episode_steps: int = 2000,
        stair_config: Optional[Dict] = None
    ):
        """
        Initialiseer traplopen RL environment
        
        Args:
            render_mode: Rendering mode ("human" of "rgb_array")
            gui: Toon PyBullet GUI
            max_episode_steps: Maximum aantal stappen per episode
            stair_config: Configuratie voor trap:
                - num_steps: Aantal treden (default: 5)
                - step_height: Hoogte per trede in meters (default: 0.15)
                - step_depth: Diepte per trede in meters (default: 0.25)
                - step_width: Breedte van trap in meters (default: 0.5)
                - start_distance: Afstand van robot tot trap in meters (default: 1.0)
        """
        super().__init__()
        
        self.render_mode = render_mode
        self.gui = gui or (render_mode == "human")
        self.max_episode_steps = max_episode_steps
        
        # Trap configuratie
        self.stair_config = stair_config or {}
        self.num_steps = self.stair_config.get("num_steps", 5)
        self.step_height = self.stair_config.get("step_height", 0.15)
        self.step_depth = self.stair_config.get("step_depth", 0.25)
        self.step_width = self.stair_config.get("step_width", 0.5)
        self.start_distance = self.stair_config.get("start_distance", 1.0)
        
        # Simulator
        self.sim = None
        self.stair_ids = []  # IDs van trap objecten
        
        # Episode tracking
        self.step_count = 0
        self.episode_reward = 0.0
        self.current_step_index = 0  # Huidige trede waar robot naartoe gaat
        self.step_positions = []  # Posities van alle treden
        
        # Define observation space
        # 12 joint pos + 12 joint vel + 3 base pos + 4 base ori + 3 base lin vel + 3 base ang vel + 3 next step pos + 1 distance
        obs_dim = 12 + 12 + 3 + 4 + 3 + 3 + 3 + 1
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
        
    def _create_stairs(self):
        """Maak trap in PyBullet"""
        if self.sim is None:
            return
        
        # Verwijder oude trap
        for stair_id in self.stair_ids:
            p.removeBody(stair_id)
        self.stair_ids = []
        self.step_positions = []
        
        # Maak trap
        for i in range(self.num_steps):
            step_x = self.start_distance + i * self.step_depth
            step_y = 0.0
            step_z = (i + 1) * self.step_height
            
            # Maak trede
            step_shape = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=[self.step_width/2, self.step_depth/2, self.step_height/2]
            )
            
            step_id = p.createMultiBody(
                baseMass=0,  # Statisch
                baseCollisionShapeIndex=step_shape,
                basePosition=[step_x, step_y, step_z]
            )
            
            # Set kleur (grijs)
            p.changeVisualShape(step_id, -1, rgbaColor=[0.5, 0.5, 0.5, 1.0])
            
            self.stair_ids.append(step_id)
            self.step_positions.append([step_x, step_y, step_z])
        
        # Maak platform bovenaan trap
        platform_x = self.start_distance + self.num_steps * self.step_depth
        platform_z = self.num_steps * self.step_height + 0.1
        platform_shape = p.createCollisionShape(
            p.GEOM_BOX,
            halfExtents=[self.step_width/2, 1.0, 0.1]
        )
        platform_id = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=platform_shape,
            basePosition=[platform_x, step_y, platform_z]
        )
        p.changeVisualShape(platform_id, -1, rgbaColor=[0.3, 0.3, 0.3, 1.0])
        self.stair_ids.append(platform_id)
        
    def _get_next_step_position(self) -> Tuple[float, float, float]:
        """Haal positie van volgende trede op"""
        if self.current_step_index < len(self.step_positions):
            return self.step_positions[self.current_step_index]
        else:
            # Platform bovenaan
            return [
                self.start_distance + self.num_steps * self.step_depth,
                0.0,
                self.num_steps * self.step_height + 0.1
            ]
    
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
        
        # Next step position
        next_step_pos = self._get_next_step_position()
        
        # Distance to next step
        distance_to_step = np.linalg.norm(
            np.array(base_pos[:2]) - np.array(next_step_pos[:2])
        )
        
        # Combineer alle observaties
        obs = np.concatenate([
            joint_positions,
            joint_velocities,
            np.array(base_pos, dtype=np.float32),
            np.array(base_ori, dtype=np.float32),
            np.array(base_lin_vel, dtype=np.float32),
            np.array(base_ang_vel, dtype=np.float32),
            np.array(next_step_pos, dtype=np.float32),
            np.array([distance_to_step], dtype=np.float32),
        ])
        
        return obs
    
    def _get_info(self) -> Dict[str, Any]:
        """Haal extra info op"""
        return {
            "step_count": self.step_count,
            "episode_reward": self.episode_reward,
            "current_step_index": self.current_step_index,
            "num_steps": self.num_steps,
        }
    
    def _update_step_index(self):
        """Update welke trede de robot moet bereiken"""
        if self.sim is None:
            return
        
        base_pos, _ = self.sim.get_base_pose()
        
        # Check of robot volgende trede heeft bereikt
        if self.current_step_index < len(self.step_positions):
            next_step_pos = self.step_positions[self.current_step_index]
            distance = np.linalg.norm(
                np.array(base_pos[:2]) - np.array(next_step_pos[:2])
            )
            
            # Als robot dichtbij genoeg is en op goede hoogte
            if distance < 0.2 and base_pos[2] > next_step_pos[2] - 0.1:
                self.current_step_index += 1
    
    def _calculate_reward(self) -> float:
        """Bereken reward voor traplopen"""
        if self.sim is None:
            return 0.0
        
        base_pos, base_ori = self.sim.get_base_pose()
        base_lin_vel, base_ang_vel = self.sim.get_base_velocity()
        joint_states = self.sim.get_joint_states()
        
        reward = 0.0
        
        # Reward voor voorwaartse beweging richting trap
        forward_velocity = base_lin_vel[0]
        reward += 5.0 * forward_velocity
        
        # Reward voor het bereiken van volgende trede
        next_step_pos = self._get_next_step_position()
        distance_to_step = np.linalg.norm(
            np.array(base_pos[:2]) - np.array(next_step_pos[:2])
        )
        
        # Beloning voor dichterbij komen
        reward += 10.0 * (1.0 / (1.0 + distance_to_step))
        
        # Grote beloning voor het bereiken van een trede
        if distance_to_step < 0.15 and base_pos[2] > next_step_pos[2] - 0.05:
            reward += 50.0
        
        # Beloning voor het bereiken van de top
        if self.current_step_index >= self.num_steps:
            reward += 100.0
        
        # Penalty voor achteruit bewegen
        if forward_velocity < -0.1:
            reward -= 10.0
        
        # Penalty voor zijwaartse beweging (stabiliteit)
        lateral_velocity = abs(base_lin_vel[1])
        reward -= 5.0 * lateral_velocity
        
        # Penalty voor rotatie (stabiliteit)
        angular_velocity_magnitude = np.linalg.norm(base_ang_vel)
        reward -= 2.0 * angular_velocity_magnitude
        
        # Penalty voor te veel hoogte variatie (moet geleidelijk omhoog)
        expected_height = self.current_step_index * self.step_height + 0.5
        height_error = abs(base_pos[2] - expected_height)
        reward -= 10.0 * height_error
        
        # Penalty voor vallen
        if base_pos[2] < 0.2:
            reward -= 100.0
        
        # Reward voor stabiliteit (lage joint velocities)
        joint_velocities = [joint_states[name]['velocity'] for name in self.sim.joint_names]
        avg_joint_velocity = np.mean(np.abs(joint_velocities))
        reward += 1.0 * (1.0 - min(avg_joint_velocity, 1.0))
        
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
        if base_pos[2] < 0.2:
            return True
        
        # Episode eindigt als robot de top heeft bereikt
        if self.current_step_index >= self.num_steps:
            return True
        
        # Episode eindigt als robot te ver achteruit gaat
        if base_pos[0] < -1.0:
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
        
        # Maak trap
        self._create_stairs()
        
        # Reset tracking
        self.step_count = 0
        self.episode_reward = 0.0
        self.current_step_index = 0
        
        # Reset robot naar start positie (voor trap)
        start_pos = [0.0, 0.0, 0.5]
        start_ori = p.getQuaternionFromEuler([0, 0, 0])
        self.sim.reset(position=start_pos, orientation=start_ori)
        
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
        
        # Update welke trede robot moet bereiken
        self._update_step_index()
        
        # Update tracking
        self.step_count += 1
        reward = self._calculate_reward()
        self.episode_reward += reward
        
        # Check done
        done = self._is_done()
        truncated = False
        
        obs = self._get_obs()
        info = self._get_info()
        
        return obs, reward, done, truncated, info
    
    def render(self):
        """Render environment"""
        if self.render_mode == "human":
            # PyBullet GUI wordt automatisch getoond als gui=True
            pass
        elif self.render_mode == "rgb_array":
            raise NotImplementedError("RGB array rendering nog niet geïmplementeerd")
    
    def close(self):
        """Sluit environment"""
        if self.sim is not None:
            # Verwijder trap
            for stair_id in self.stair_ids:
                p.removeBody(stair_id)
            self.stair_ids = []
            
            self.sim.close()
            self.sim = None

