"""
RL Controller voor Unitree Go2 Robot

Laadt getrainde RL modellen en gebruikt ze om de fysieke Go2 robot te controleren.
"""

import numpy as np
from typing import Optional, Dict, List, Any
from pathlib import Path
import os

try:
    from stable_baselines3 import PPO, SAC, TD3
except ImportError:
    raise ImportError(
        "Stable-Baselines3 niet geïnstalleerd. Installeer met: pip install stable-baselines3"
    )

from .robot import Go2Robot


class Go2RLController:
    """
    Controller die getrainde RL modellen gebruikt om Go2 robot te besturen
    """
    
    def __init__(
        self,
        robot: Go2Robot,
        model_path: str,
        observation_normalizer: Optional[Dict] = None
    ):
        """
        Initialiseer RL controller
        
        Args:
            robot: Go2Robot instantie
            model_path: Pad naar getraind RL model
            observation_normalizer: Normalisatie parameters voor observaties (optioneel)
        """
        self.robot = robot
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model niet gevonden: {self.model_path}")
        
        # Laad model
        print(f"✓ RL model laden: {self.model_path}")
        self.model = self._load_model(self.model_path)
        
        # Normalisatie (optioneel)
        self.observation_normalizer = observation_normalizer
        
        # Tracking
        self.step_count = 0
        
    def _load_model(self, model_path: Path):
        """Laad RL model"""
        # Probeer automatisch type te detecteren
        try:
            return PPO.load(str(model_path))
        except:
            try:
                return SAC.load(str(model_path))
            except:
                try:
                    return TD3.load(str(model_path))
                except Exception as e:
                    raise ValueError(f"Kon model niet laden: {e}")
    
    def _get_observation(self) -> np.ndarray:
        """
        Haal observation op van fysieke robot
        
        Returns:
            Observation array (37 of 41 dimensies afhankelijk van model type)
        """
        # Haal robot state op
        state = self.robot.get_state()
        
        # Joint states
        joint_positions = []
        joint_velocities = []
        
        # Extract joint data (aanpassen aan daadwerkelijke robot API)
        # Dit is een placeholder - moet aangepast worden aan echte Go2 API
        if hasattr(state, 'joint_positions'):
            joint_positions = state.joint_positions[:12]  # 12 joints
            joint_velocities = state.joint_velocities[:12] if hasattr(state, 'joint_velocities') else [0.0] * 12
        else:
            # Fallback: gebruik default waarden
            joint_positions = [0.0] * 12
            joint_velocities = [0.0] * 12
        
        # Base pose (aanpassen aan echte API)
        base_pos = [0.0, 0.0, 0.5]  # Placeholder
        base_ori = [0.0, 0.0, 0.0, 1.0]  # Placeholder quaternion
        base_lin_vel = [0.0, 0.0, 0.0]
        base_ang_vel = [0.0, 0.0, 0.0]
        
        # Combineer observaties
        obs = np.concatenate([
            np.array(joint_positions, dtype=np.float32),
            np.array(joint_velocities, dtype=np.float32),
            np.array(base_pos, dtype=np.float32),
            np.array(base_ori, dtype=np.float32),
            np.array(base_lin_vel, dtype=np.float32),
            np.array(base_ang_vel, dtype=np.float32),
        ])
        
        # Voeg extra dimensies toe voor traplopen model (als nodig)
        if len(obs) == 37:
            # Traplopen model heeft 41 dimensies (extra: next step pos + distance)
            # Voor normale operatie: geen trap, dus default waarden
            next_step_pos = [0.0, 0.0, 0.0]
            distance_to_step = 0.0
            obs = np.concatenate([
                obs,
                np.array(next_step_pos, dtype=np.float32),
                np.array([distance_to_step], dtype=np.float32),
            ])
        
        # Normaliseer indien nodig
        if self.observation_normalizer:
            obs_mean = self.observation_normalizer.get('mean', np.zeros_like(obs))
            obs_std = self.observation_normalizer.get('std', np.ones_like(obs))
            obs = (obs - obs_mean) / (obs_std + 1e-8)
        
        return obs
    
    def _scale_action_to_joints(self, action: np.ndarray) -> Dict[str, float]:
        """
        Scale action van [-1, 1] naar joint posities
        
        Args:
            action: Action array van model (12 dimensies)
            
        Returns:
            Dictionary met joint naam -> positie
        """
        # Joint limits (aanpassen aan echte Go2 limits)
        joint_limits = np.array([
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
        
        # Scale actions
        scaled_actions = {}
        joint_names = [
            'FL_hip_joint', 'FL_thigh_joint', 'FL_calf_joint',
            'FR_hip_joint', 'FR_thigh_joint', 'FR_calf_joint',
            'RL_hip_joint', 'RL_thigh_joint', 'RL_calf_joint',
            'RR_hip_joint', 'RR_thigh_joint', 'RR_calf_joint',
        ]
        
        for i, joint_name in enumerate(joint_names):
            if i < len(action):
                low, high = joint_limits[i]
                scaled_value = low + (action[i] + 1.0) / 2.0 * (high - low)
                scaled_actions[joint_name] = float(scaled_value)
        
        return scaled_actions
    
    def step(self, deterministic: bool = True) -> Dict[str, Any]:
        """
        Voer één RL stap uit
        
        Args:
            deterministic: Gebruik deterministische policy (True) of stochastisch (False)
            
        Returns:
            Dictionary met info over de stap
        """
        # Haal observation op
        obs = self._get_observation()
        
        # Predict action
        action, _ = self.model.predict(obs, deterministic=deterministic)
        
        # Scale naar joint posities
        joint_targets = self._scale_action_to_joints(action)
        
        # Stuur commando naar robot
        # Aanpassen aan echte Go2 API
        # self.robot.set_joint_positions(joint_targets)
        
        self.step_count += 1
        
        return {
            "step_count": self.step_count,
            "action": action,
            "joint_targets": joint_targets,
        }
    
    def run_episode(self, max_steps: int = 1000, frequency: float = 20.0):
        """
        Voer een episode uit
        
        Args:
            max_steps: Maximum aantal stappen
            frequency: Control frequentie in Hz
        """
        import time
        
        step_time = 1.0 / frequency
        
        print(f"✓ Episode starten (max {max_steps} stappen @ {frequency}Hz)")
        
        for step in range(max_steps):
            start_time = time.time()
            
            # RL stap
            info = self.step()
            
            # Wacht tot volgende stap
            elapsed = time.time() - start_time
            sleep_time = max(0, step_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            if step % 100 == 0:
                print(f"  Step {step}/{max_steps}")
        
        print("✓ Episode voltooid")


class Go2ModelManager:
    """
    Beheer meerdere RL modellen voor Go2 robot
    """
    
    def __init__(self, robot: Go2Robot, models_dir: str = "models"):
        """
        Initialiseer model manager
        
        Args:
            robot: Go2Robot instantie
            models_dir: Directory met getrainde modellen
        """
        self.robot = robot
        self.models_dir = Path(models_dir)
        self.models: Dict[str, Go2RLController] = {}
        self.current_model: Optional[str] = None
        
    def load_model(self, name: str, model_path: str, **kwargs) -> Go2RLController:
        """
        Laad een RL model
        
        Args:
            name: Naam voor het model (bijv. "walking", "stairs")
            model_path: Pad naar model bestand
            **kwargs: Extra argumenten voor Go2RLController
            
        Returns:
            Go2RLController instantie
        """
        print(f"✓ Model laden: {name} van {model_path}")
        controller = Go2RLController(self.robot, model_path, **kwargs)
        self.models[name] = controller
        return controller
    
    def load_from_directory(self, name: str, model_dir: str, model_file: str = "best_model.zip", **kwargs):
        """
        Laad model uit directory
        
        Args:
            name: Naam voor het model
            model_dir: Directory met model (bijv. "models/go2_rl")
            model_file: Model bestandsnaam (default: "best_model.zip")
            **kwargs: Extra argumenten voor Go2RLController
        """
        model_path = Path(model_dir) / "best_model" / model_file
        if not model_path.exists():
            # Probeer alternatieve locaties
            alt_paths = [
                Path(model_dir) / model_file,
                Path(model_dir) / "final_model.zip",
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    model_path = alt_path
                    break
        
        return self.load_model(name, str(model_path), **kwargs)
    
    def switch_model(self, name: str) -> Go2RLController:
        """
        Wissel naar ander model
        
        Args:
            name: Naam van model om naar te wisselen
            
        Returns:
            Go2RLController instantie
        """
        if name not in self.models:
            raise ValueError(f"Model '{name}' niet geladen. Beschikbare modellen: {list(self.models.keys())}")
        
        self.current_model = name
        print(f"✓ Gewisseld naar model: {name}")
        return self.models[name]
    
    def get_current_controller(self) -> Optional[Go2RLController]:
        """Haal huidige controller op"""
        if self.current_model is None:
            return None
        return self.models.get(self.current_model)
    
    def list_models(self) -> List[str]:
        """Lijst alle geladen modellen"""
        return list(self.models.keys())
    
    def unload_model(self, name: str):
        """Unload een model"""
        if name in self.models:
            del self.models[name]
            if self.current_model == name:
                self.current_model = None
            print(f"✓ Model '{name}' verwijderd")

