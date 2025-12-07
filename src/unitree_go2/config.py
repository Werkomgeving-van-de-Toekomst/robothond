"""
Configuratie loader voor Unitree Go2 EDU

Laadt configuratie uit YAML bestanden.
"""

import yaml
import os
from typing import Dict, Any
from pathlib import Path


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Laad configuratie uit YAML bestand
    
    Args:
        config_path: Pad naar config bestand. Als None, gebruikt default locatie.
        
    Returns:
        Dictionary met configuratie
    """
    if config_path is None:
        # Zoek config in project root
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "robot_config.yaml"
    
    if not os.path.exists(config_path):
        # Gebruik default configuratie
        return get_default_config()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_default_config() -> Dict[str, Any]:
    """Retourneer standaard configuratie"""
    return {
        "robot": {
            "ip_address": "192.168.123.161",
            "sdk_port": 8080,
            "timeout": 5.0
        },
        "movement": {
            "default_speed": 0.5,
            "default_angular_velocity": 0.5
        },
        "sensors": {
            "update_rate": 20,
            "enabled": ["imu", "joint_states", "battery"]
        },
        "safety": {
            "max_speed": 1.0,
            "emergency_stop_enabled": True
        }
    }

