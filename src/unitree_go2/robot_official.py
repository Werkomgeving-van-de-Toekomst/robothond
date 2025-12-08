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
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
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
            # Initialiseer DDS channel factory met netwerk interface
            ChannelFactoryInitialize(0, self.network_interface)
            
            # Initialiseer sport client (voor beweging)
            self.sport_client = SportClient()
            self.sport_client.SetTimeout(self.timeout)
            self.sport_client.Init()
            
            # Initialiseer robot state client (voor sensor data)
            self.robot_state_client = RobotStateClient()
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
            # Gebruik officiële SDK StandUp methode
            code = self.sport_client.StandUp()
            if code != 0:
                raise Go2CommandError(f"Stand commando mislukt met code: {code}")
            
            return {"status": "ok", "message": "Stand command sent", "code": code}
            
        except Exception as e:
            raise Go2CommandError(f"Fout bij stand commando: {e}")
    
    def sit(self):
        """Laat robot zitten"""
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
        
        try:
            # Gebruik officiële SDK StandDown methode
            code = self.sport_client.StandDown()
            if code != 0:
                raise Go2CommandError(f"Sit commando mislukt met code: {code}")
            
            return {"status": "ok", "message": "Sit command sent", "code": code}
            
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
            # Gebruik officiële SDK Move methode
            code = self.sport_client.Move(vx, vy, vyaw)
            if code != 0:
                raise Go2CommandError(f"Move commando mislukt met code: {code}")
            
            return {"status": "ok", "message": "Move command sent", "code": code}
            
        except Exception as e:
            raise Go2CommandError(f"Fout bij move commando: {e}")
    
    def stop(self):
        """Stop alle beweging"""
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
        
        try:
            # Gebruik officiële SDK StopMove methode
            code = self.sport_client.StopMove()
            if code != 0:
                raise Go2CommandError(f"Stop commando mislukt met code: {code}")
            
            return {"status": "ok", "message": "Stop command sent", "code": code}
        except Exception as e:
            raise Go2CommandError(f"Fout bij stop commando: {e}")
    
    def get_state(self) -> Dict[str, Any]:
        """
        Haal robot status op
        
        Returns:
            Dictionary met robot status informatie
            
        Note: Officiële SDK gebruikt subscription model voor state.
        Deze implementatie is een vereenvoudigde versie.
        """
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
        
        try:
            # Officiële SDK gebruikt subscription model voor robot state
            # Voor nu retourneren we een basis state structuur
            # Voor volledige state, gebruik RobotStateClient subscription
            
            result = {
                "battery_level": 0,  # Vereist subscription om te lezen
                "base_position": [0.0, 0.0, 0.0],
                "base_orientation": [1.0, 0.0, 0.0, 0.0],
                "base_linear_velocity": [0.0, 0.0, 0.0],
                "base_angular_velocity": [0.0, 0.0, 0.0],
                "joint_positions": {},
                "joint_velocities": {},
                "imu_data": {},
                "note": "Gebruik RobotStateClient subscription voor volledige state"
            }
            
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

