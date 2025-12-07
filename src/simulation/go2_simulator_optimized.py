"""
Geoptimaliseerde PyBullet Simulator voor Apple Silicon M3 Max

Gebruikt deze versie voor betere rendering performance op Apple Silicon.
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import platform

try:
    import pybullet as p
    import pybullet_data
except ImportError:
    raise ImportError(
        "PyBullet niet geïnstalleerd. Installeer met: conda install -c conda-forge pybullet"
    )


class Go2SimulatorOptimized:
    """Geoptimaliseerde PyBullet simulator voor Apple Silicon"""
    
    def __init__(
        self,
        urdf_path: Optional[str] = None,
        gui: bool = True,
        gravity: float = -9.81,
        timestep: float = 1.0 / 240.0,
        render_fps: int = 30  # Lagere rendering FPS voor betere performance
    ):
        """
        Initialiseer geoptimaliseerde PyBullet simulator
        
        Args:
            urdf_path: Pad naar URDF bestand (None = gebruik default)
            gui: Toon GUI (True) of headless (False)
            gravity: Zwaartekracht waarde
            timestep: Simulatie tijdstap in seconden (physics blijft op 240Hz)
            render_fps: Rendering frames per seconde (30 voor betere performance)
        """
        # Bepaal URDF pad
        if urdf_path is None:
            project_root = Path(__file__).parent.parent.parent
            urdf_path = project_root / "urdf" / "urdf" / "go2_description.urdf"
        
        self.urdf_path = Path(urdf_path)
        if not self.urdf_path.exists():
            raise FileNotFoundError(f"URDF bestand niet gevonden: {self.urdf_path}")
        
        self.render_fps = render_fps
        self.render_interval = 1.0 / render_fps
        self.last_render_time = 0.0
        
        # Start PyBullet met optimalisaties voor Apple Silicon
        if gui:
            # Gebruik GUI met optimalisaties
            self.client = p.connect(p.GUI)
            
            # Apple Silicon optimalisaties
            self._configure_apple_silicon_rendering()
        else:
            self.client = p.connect(p.DIRECT)
        
        # Configureer simulator
        p.setGravity(0, 0, gravity)
        p.setTimeStep(timestep)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        
        # Optimaliseer physics engine
        self._configure_physics_engine()
        
        # Laad vloer
        self.plane_id = p.loadURDF("plane.urdf")
        
        # Laad robot
        start_pos = [0, 0, 0.5]
        start_orientation = p.getQuaternionFromEuler([0, 0, 0])
        
        # Fix URDF paths
        urdf_dir = self.urdf_path.parent.parent
        import re
        import tempfile
        
        urdf_content = self.urdf_path.read_text(encoding='utf-8')
        urdf_content = re.sub(
            r'package://go2_description/dae/([^"]+)',
            lambda m: str((urdf_dir / "dae" / m.group(1)).absolute()),
            urdf_content
        )
        urdf_content = re.sub(
            r'package://go2_description/meshes/([^"]+)',
            lambda m: str((urdf_dir / "meshes" / m.group(1)).absolute()),
            urdf_content
        )
        
        temp_urdf = tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False, encoding='utf-8')
        temp_urdf.write(urdf_content)
        temp_urdf.close()
        
        try:
            self.robot_id = p.loadURDF(
                temp_urdf.name,
                start_pos,
                start_orientation,
                flags=p.URDF_USE_INERTIA_FROM_FILE | p.URDF_USE_MATERIAL_COLORS_FROM_MTL
            )
        finally:
            import os
            if os.path.exists(temp_urdf.name):
                os.unlink(temp_urdf.name)
        
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
        
        self.default_joint_positions = self._get_default_joint_positions()
        self.reset()
        
        print(f"✓ Robot geladen: {len(self.joint_indices)} actuated joints (Apple Silicon geoptimaliseerd)")
    
    def _configure_apple_silicon_rendering(self):
        """Configureer rendering voor Apple Silicon optimalisatie"""
        # Disable onnodige visualisaties
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)  # Geen GUI controls
        p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 0)  # Geen shadows (snelste)
        p.configureDebugVisualizer(p.COV_ENABLE_TINY_RENDERER, 0)  # Gebruik main renderer
        p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
        p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
        p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)
        
        # Set camera positie voor betere view
        p.resetDebugVisualizerCamera(
            cameraDistance=2.0,
            cameraYaw=45,
            cameraPitch=-20,
            cameraTargetPosition=[0, 0, 0.5]
        )
    
    def _configure_physics_engine(self):
        """Configureer physics engine voor betere performance"""
        p.setPhysicsEngineParameter(
            numSolverIterations=10,  # Verlaag voor snellere physics
            useSplitImpulse=1,
            splitImpulsePenetrationThreshold=-0.02,
            enableConeFriction=0,  # Disable voor betere performance
            deterministicOverlappingPairs=0,  # Sneller
            numSubSteps=0  # Geen substeps voor betere performance
        )
    
    def step(self, steps: int = 1, render: bool = True):
        """
        Voer simulatie stappen uit met geoptimaliseerde rendering
        
        Args:
            steps: Aantal stappen
            render: Of rendering moet worden uitgevoerd (True = alleen op render_fps)
        """
        import time
        current_time = time.time()
        
        for _ in range(steps):
            p.stepSimulation()
            
            # Render alleen op ingestelde FPS voor betere performance
            if render and (current_time - self.last_render_time) >= self.render_interval:
                # Rendering gebeurt automatisch door PyBullet
                self.last_render_time = current_time
    
    def _get_default_joint_positions(self) -> List[float]:
        """Retourneer standaard joint posities"""
        default_positions = []
        for i in range(len(self.joint_indices)):
            if 'hip' in self.joint_names[i].lower():
                default_positions.append(0.0)
            elif 'thigh' in self.joint_names[i].lower():
                default_positions.append(0.4)
            elif 'calf' in self.joint_names[i].lower():
                default_positions.append(-0.8)
            else:
                default_positions.append(0.0)
        return default_positions
    
    def reset(self, position: Optional[List[float]] = None, orientation: Optional[List[float]] = None):
        """Reset robot naar beginpositie"""
        if position is None:
            position = [0, 0, 0.5]
        if orientation is None:
            orientation = p.getQuaternionFromEuler([0, 0, 0])
        
        p.resetBasePositionAndOrientation(self.robot_id, position, orientation)
        
        for i, joint_idx in enumerate(self.joint_indices):
            p.resetJointState(
                self.robot_id,
                joint_idx,
                self.default_joint_positions[i] if i < len(self.default_joint_positions) else 0.0
            )
        
        p.resetBaseVelocity(self.robot_id, [0, 0, 0], [0, 0, 0])
        for joint_idx in self.joint_indices:
            p.resetJointState(self.robot_id, joint_idx, targetValue=0, targetVelocity=0)
    
    def set_joint_targets(self, targets: Dict[str, float], forces: Optional[Dict[str, float]] = None):
        """Stel joint targets in"""
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
        """Haal joint states op"""
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
        """Haal base positie en orientatie op"""
        pose = p.getBasePositionAndOrientation(self.robot_id)
        return pose[0], pose[1]
    
    def get_base_velocity(self) -> Tuple[List[float], List[float]]:
        """Haal base snelheid op"""
        velocity = p.getBaseVelocity(self.robot_id)
        return velocity[0], velocity[1]
    
    def close(self):
        """Sluit simulator"""
        p.disconnect(self.client)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

