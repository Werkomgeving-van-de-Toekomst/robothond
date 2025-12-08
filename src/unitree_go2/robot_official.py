"""
Unitree Go2 EDU Robot Interface - Officiële SDK Wrapper

Wrapper rondom de officiële unitree_sdk2_python SDK die compatibel is
met onze bestaande Go2Robot API.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import time

# Voeg officiële SDK toe aan path
sdk_path = Path(__file__).parent.parent.parent.parent / "unitree_sdk2_python"
if sdk_path.exists():
    sys.path.insert(0, str(sdk_path))

try:
    from unitree_sdk2py.go2.sport.sport_client import SportClient
    from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient
    from unitree_sdk2py.idl.unitree_go import msg as go_msg
    HAS_OFFICIAL_SDK = True
except ImportError:
    HAS_OFFICIAL_SDK = False

from .exceptions import Go2ConnectionError, Go2CommandError, Go2TimeoutError


class Go2RobotOfficial:
    """
    Wrapper rondom officiële unitree_sdk2_python SDK
    
    Behoudt compatibiliteit met onze bestaande Go2Robot API.
    """
    
    def __init__(self, ip_address: str = "192.168.123.161", port: int = 8080, timeout: float = 5.0, network_interface: Optional[str] = None):
        """
        Initialiseer Go2 robot verbinding met officiële SDK
        
        Args:
            ip_address: IP adres van de robot (voor referentie)
            port: Poort (niet gebruikt met officiële SDK)
            timeout: Timeout in seconden
            network_interface: Netwerk interface naam (bijv. "en0", "eth0")
                              Als None, wordt automatisch gedetecteerd
        """
        if not HAS_OFFICIAL_SDK:
            raise ImportError(
                "Officiële SDK niet gevonden. Zorg dat unitree_sdk2_python "
                "geïnstalleerd is in unitree_sdk2_python/ directory."
            )
        
        self.ip_address = ip_address
        self.timeout = timeout
        self.network_interface = network_interface or self._detect_network_interface()
        
        # SDK clients
        self.sport_client: Optional[SportClient] = None
        self.robot_state_client: Optional[RobotStateClient] = None
        
        self.connected = False
    
    def _detect_network_interface(self) -> str:
        """
        Detecteer netwerk interface automatisch
        
        Returns:
            Interface naam (bijv. "en0", "eth0")
        """
        import platform
        import subprocess
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Probeer WiFi interface
            try:
                result = subprocess.run(
                    ["route", "get", "default"],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split('\n'):
                    if 'interface:' in line:
                        return line.split(':')[1].strip()
            except:
                pass
            return "en0"  # Fallback voor macOS
        elif system == "Linux":
            # Probeer eerste actieve interface
            try:
                result = subprocess.run(
                    ["ip", "route", "get", "8.8.8.8"],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split('\n'):
                    if 'dev' in line:
                        parts = line.split()
                        if 'dev' in parts:
                            idx = parts.index('dev')
                            if idx + 1 < len(parts):
                                return parts[idx + 1]
            except:
                pass
            return "eth0"  # Fallback voor Linux
        else:
            return "eth0"  # Fallback
    
    def connect(self) -> bool:
        """
        Maak verbinding met de robot via officiële SDK
        
        Returns:
            True als verbinding succesvol is
            
        Raises:
            Go2ConnectionError: Als verbinding mislukt
        """
        try:
            # Initialiseer sport client (voor beweging)
            self.sport_client = SportClient(self.network_interface)
            self.sport_client.SetTimeout(self.timeout)
            self.sport_client.Init()
            
            # Initialiseer robot state client (voor sensor data)
            self.robot_state_client = RobotStateClient(self.network_interface)
            self.robot_state_client.SetTimeout(self.timeout)
            self.robot_state_client.Init()
            
            self.connected = True
            print(f"✓ Verbonden via officiële SDK (interface: {self.network_interface})")
            return True
            
        except Exception as e:
            self.connected = False
            raise Go2ConnectionError(f"Kon niet verbinden met robot via officiële SDK: {e}")
    
    def disconnect(self):
        """Verbreek verbinding met de robot"""
        if self.sport_client:
            # Officiële SDK heeft geen expliciete disconnect
            self.sport_client = None
        
        if self.robot_state_client:
            self.robot_state_client = None
        
        self.connected = False
    
    def stand(self):
        """Laat robot rechtop staan"""
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
        
        try:
            # Gebruik officiële SDK stand commando
            req = go_msg.Request()
            req.RequestId = 1
            req.RequestType = go_msg.Request.RequestTypeEnum.STAND
            
            code = self.sport_client.Request(req)
            if code != 0:
                raise Go2CommandError(f"Stand commando mislukt met code: {code}")
            
            return {"status": "ok", "message": "Stand command sent"}
            
        except Exception as e:
            raise Go2CommandError(f"Fout bij stand commando: {e}")
    
    def sit(self):
        """Laat robot zitten"""
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
        
        try:
            req = go_msg.Request()
            req.RequestId = 1
            req.RequestType = go_msg.Request.RequestTypeEnum.DOWN
            
            code = self.sport_client.Request(req)
            if code != 0:
                raise Go2CommandError(f"Sit commando mislukt met code: {code}")
            
            return {"status": "ok", "message": "Sit command sent"}
            
        except Exception as e:
            raise Go2CommandError(f"Fout bij sit commando: {e}")
    
    def move(self, vx: float = 0.0, vy: float = 0.0, vyaw: float = 0.0):
        """
        Beweeg robot met opgegeven snelheden
        
        Args:
            vx: Snelheid vooruit/achteruit (m/s)
            vy: Snelheid links/rechts (m/s)
            vyaw: Draaisnelheid (rad/s)
        """
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
        
        try:
            # Maak velocity commando
            req = go_msg.Request()
            req.RequestId = 1
            req.RequestType = go_msg.Request.RequestTypeEnum.VELOCITY
            
            # Set velocity parameters
            req.Velocity = go_msg.Velocity()
            req.Velocity.VelocityX = vx
            req.Velocity.VelocityY = vy
            req.Velocity.VelocityYaw = vyaw
            
            code = self.sport_client.Request(req)
            if code != 0:
                raise Go2CommandError(f"Move commando mislukt met code: {code}")
            
            return {"status": "ok", "message": "Move command sent"}
            
        except Exception as e:
            raise Go2CommandError(f"Fout bij move commando: {e}")
    
    def stop(self):
        """Stop alle beweging"""
        return self.move(0.0, 0.0, 0.0)
    
    def get_state(self) -> Dict[str, Any]:
        """
        Haal robot status op
        
        Returns:
            Dictionary met robot status informatie
        """
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
        
        try:
            # Haal robot state op
            state = go_msg.State()
            code = self.robot_state_client.GetState(state)
            
            if code != 0:
                raise Go2CommandError(f"Get state mislukt met code: {code}")
            
            # Converteer naar ons formaat
            result = {
                "battery_level": getattr(state, 'BatteryState', {}).get('BatteryPercent', 0) if hasattr(state, 'BatteryState') else 0,
                "base_position": [
                    getattr(state, 'Position', [0, 0, 0])[0] if hasattr(state, 'Position') else 0.0,
                    getattr(state, 'Position', [0, 0, 0])[1] if hasattr(state, 'Position') else 0.0,
                    getattr(state, 'Position', [0, 0, 0])[2] if hasattr(state, 'Position') else 0.0,
                ],
                "base_orientation": [1.0, 0.0, 0.0, 0.0],  # Quaternion
                "base_linear_velocity": [0.0, 0.0, 0.0],
                "base_angular_velocity": [0.0, 0.0, 0.0],
                "joint_positions": {},
                "joint_velocities": {},
                "imu_data": {}
            }
            
            # Probeer joint data te extraheren (afhankelijk van SDK versie)
            if hasattr(state, 'JointState'):
                for i, joint_state in enumerate(state.JointState):
                    joint_name = f"joint_{i}"
                    result["joint_positions"][joint_name] = getattr(joint_state, 'Position', 0.0)
                    result["joint_velocities"][joint_name] = getattr(joint_state, 'Velocity', 0.0)
            
            return result
            
        except Exception as e:
            raise Go2CommandError(f"Fout bij ophalen state: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

