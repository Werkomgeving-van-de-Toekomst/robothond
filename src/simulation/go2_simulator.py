"""
PyBullet Simulator voor Unitree Go2 EDU

Simuleert de Go2 robot in PyBullet voor testing en ontwikkeling.
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

try:
    import pybullet as p
    import pybullet_data
except ImportError:
    raise ImportError(
        "PyBullet niet geïnstalleerd. Installeer met: pip install pybullet"
    )


class Go2Simulator:
    """PyBullet simulator voor Unitree Go2 robot"""
    
    def __init__(
        self,
        urdf_path: Optional[str] = None,
        gui: bool = True,
        gravity: float = -9.81,
        timestep: float = 1.0 / 240.0
    ):
        """
        Initialiseer PyBullet simulator
        
        Args:
            urdf_path: Pad naar URDF bestand (None = gebruik default)
            gui: Toon GUI (True) of headless (False)
            gravity: Zwaartekracht waarde
            timestep: Simulatie tijdstap in seconden
        """
        # Bepaal URDF pad
        if urdf_path is None:
            project_root = Path(__file__).parent.parent.parent
            urdf_path = project_root / "urdf" / "urdf" / "go2_description.urdf"
        
        self.urdf_path = Path(urdf_path)
        if not self.urdf_path.exists():
            raise FileNotFoundError(f"URDF bestand niet gevonden: {self.urdf_path}")
        
        # Start PyBullet
        if gui:
            self.client = p.connect(p.GUI)
        else:
            self.client = p.connect(p.DIRECT)
        
        # Configureer simulator
        p.setGravity(0, 0, gravity)
        p.setTimeStep(timestep)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        
        # Laad vloer
        self.plane_id = p.loadURDF("plane.urdf")
        
        # Laad robot
        start_pos = [0, 0, 0.5]  # Start positie (zodat robot op vloer staat)
        start_orientation = p.getQuaternionFromEuler([0, 0, 0])
        
        # Fix mesh paths in URDF voor PyBullet
        urdf_path_str = str(self.urdf_path.absolute())
        
        self.robot_id = p.loadURDF(
            urdf_path_str,
            start_pos,
            start_orientation,
            flags=p.URDF_USE_INERTIA_FROM_FILE
        )
        
        # Haal joint informatie op
        self.joint_indices = []
        self.joint_names = []
        self.joint_lower_limits = []
        self.joint_upper_limits = []
        
        num_joints = p.getNumJoints(self.robot_id)
        for i in range(num_joints):
            joint_info = p.getJointInfo(self.robot_id, i)
            if joint_info[2] == p.JOINT_REVOLUTE or joint_info[2] == p.JOINT_PRISMATIC:
                self.joint_indices.append(i)
                self.joint_names.append(joint_info[1].decode('utf-8'))
                self.joint_lower_limits.append(joint_info[8])
                self.joint_upper_limits.append(joint_info[9])
        
        # Standaard joint posities (staande positie)
        self.default_joint_positions = self._get_default_joint_positions()
        
        # Reset naar standaard positie
        self.reset()
        
        print(f"✓ Robot geladen: {len(self.joint_indices)} actuated joints")
        print(f"  Joints: {', '.join(self.joint_names[:6])}...")
    
    def _get_default_joint_positions(self) -> List[float]:
        """Retourneer standaard joint posities voor staande houding"""
        # Go2 heeft 12 actuated joints (3 per been x 4 benen)
        # FL (Front Left): FL_hip_joint, FL_thigh_joint, FL_calf_joint
        # FR (Front Right): FR_hip_joint, FR_thigh_joint, FR_calf_joint
        # RL (Rear Left): RL_hip_joint, RL_thigh_joint, RL_calf_joint
        # RR (Rear Right): RR_hip_joint, RR_thigh_joint, RR_calf_joint
        
        # Standaard staande positie (ongeveer)
        default_positions = []
        for i in range(len(self.joint_indices)):
            # Hip joints: iets naar buiten
            if 'hip' in self.joint_names[i].lower():
                default_positions.append(0.0)
            # Thigh joints: iets naar voren
            elif 'thigh' in self.joint_names[i].lower():
                default_positions.append(0.4)
            # Calf joints: strekken
            elif 'calf' in self.joint_names[i].lower():
                default_positions.append(-0.8)
            else:
                default_positions.append(0.0)
        
        return default_positions
    
    def reset(self, position: Optional[List[float]] = None, orientation: Optional[List[float]] = None):
        """
        Reset robot naar beginpositie
        
        Args:
            position: [x, y, z] positie (None = default)
            orientation: [x, y, z, w] quaternion (None = default)
        """
        if position is None:
            position = [0, 0, 0.5]
        if orientation is None:
            orientation = p.getQuaternionFromEuler([0, 0, 0])
        
        # Reset base positie
        p.resetBasePositionAndOrientation(self.robot_id, position, orientation)
        
        # Reset joint posities
        for i, joint_idx in enumerate(self.joint_indices):
            p.resetJointState(
                self.robot_id,
                joint_idx,
                self.default_joint_positions[i] if i < len(self.default_joint_positions) else 0.0
            )
        
        # Reset velocities
        p.resetBaseVelocity(self.robot_id, [0, 0, 0], [0, 0, 0])
        for joint_idx in self.joint_indices:
            p.resetJointState(self.robot_id, joint_idx, targetValue=0, targetVelocity=0)
    
    def set_joint_positions(self, positions: Dict[str, float]):
        """
        Stel joint posities in
        
        Args:
            positions: Dictionary met joint naam -> positie (radians)
        """
        for joint_name, position in positions.items():
            if joint_name in self.joint_names:
                idx = self.joint_names.index(joint_name)
                joint_idx = self.joint_indices[idx]
                p.resetJointState(self.robot_id, joint_idx, position)
    
    def set_joint_targets(self, targets: Dict[str, float], forces: Optional[Dict[str, float]] = None):
        """
        Stel joint targets in voor position control
        
        Args:
            targets: Dictionary met joint naam -> target positie (radians)
            forces: Dictionary met joint naam -> max kracht (None = default)
        """
        for joint_name, target in targets.items():
            if joint_name in self.joint_names:
                idx = self.joint_names.index(joint_name)
                joint_idx = self.joint_indices[idx]
                max_force = forces[joint_name] if forces and joint_name in forces else 100.0
                p.setJointMotorControl2(
                    self.robot_id,
                    joint_idx,
                    p.POSITION_CONTROL,
                    targetPosition=target,
                    force=max_force
                )
    
    def get_joint_states(self) -> Dict[str, Dict[str, float]]:
        """
        Haal joint states op
        
        Returns:
            Dictionary met joint naam -> {position, velocity, effort}
        """
        states = {}
        for i, joint_name in enumerate(self.joint_names):
            joint_idx = self.joint_indices[i]
            joint_state = p.getJointState(self.robot_id, joint_idx)
            states[joint_name] = {
                'position': joint_state[0],
                'velocity': joint_state[1],
                'effort': joint_state[3]
            }
        return states
    
    def get_base_pose(self) -> Tuple[List[float], List[float]]:
        """
        Haal base positie en orientatie op
        
        Returns:
            (position [x,y,z], orientation quaternion [x,y,z,w])
        """
        pose = p.getBasePositionAndOrientation(self.robot_id)
        return pose[0], pose[1]
    
    def get_base_velocity(self) -> Tuple[List[float], List[float]]:
        """
        Haal base snelheid op
        
        Returns:
            (linear velocity [x,y,z], angular velocity [x,y,z])
        """
        velocity = p.getBaseVelocity(self.robot_id)
        return velocity[0], velocity[1]
    
    def step(self, steps: int = 1):
        """
        Voer simulatie stappen uit
        
        Args:
            steps: Aantal stappen
        """
        for _ in range(steps):
            p.stepSimulation()
    
    def run_simulation(self, duration: float, callback: Optional[callable] = None):
        """
        Voer simulatie uit voor bepaalde duur
        
        Args:
            duration: Duur in seconden
            callback: Functie die elke stap wordt aangeroepen (optioneel)
        """
        timestep = p.getPhysicsEngineParameters()['fixedTimeStep']
        steps = int(duration / timestep)
        
        for step in range(steps):
            if callback:
                callback(step, self)
            self.step()
    
    def add_debug_line(self, start: List[float], end: List[float], color: List[float] = [1, 0, 0], line_width: float = 2.0):
        """
        Teken debug lijn
        
        Args:
            start: Start positie [x, y, z]
            end: Eind positie [x, y, z]
            color: Kleur [r, g, b]
            line_width: Lijn breedte
        """
        p.addUserDebugLine(start, end, color, lineWidth=line_width)
    
    def close(self):
        """Sluit simulator"""
        p.disconnect(self.client)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

