"""
Unitree Go2 EDU Robot Interface

Basis implementatie voor communicatie met de Go2 EDU robot.
"""

import socket
import json
import time
from typing import Optional, Dict, Any
from .exceptions import Go2ConnectionError, Go2CommandError, Go2TimeoutError


class Go2Robot:
    """Hoofdklasse voor interactie met Unitree Go2 EDU robot"""
    
    def __init__(self, ip_address: str = "192.168.123.161", port: int = 8080, timeout: float = 5.0):
        """
        Initialiseer Go2 robot verbinding
        
        Args:
            ip_address: IP adres van de robot
            port: Poort voor SDK communicatie
            timeout: Timeout in seconden
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self.connected = False
    
    def connect(self) -> bool:
        """
        Maak verbinding met de robot
        
        Returns:
            True als verbinding succesvol is
            
        Raises:
            Go2ConnectionError: Als verbinding mislukt
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise Go2ConnectionError(f"Kon niet verbinden met robot: {e}")
    
    def disconnect(self):
        """Verbreek verbinding met de robot"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False
    
    def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verstuur commando naar robot
        
        Args:
            command: Commando dictionary
            
        Returns:
            Antwoord van de robot
            
        Raises:
            Go2CommandError: Als commando mislukt
            Go2TimeoutError: Als timeout optreedt
        """
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
        
        try:
            # Converteer commando naar JSON
            message = json.dumps(command).encode('utf-8')
            
            # Verstuur naar robot
            self.socket.sendto(message, (self.ip_address, self.port))
            
            # Wacht op antwoord (indien nodig)
            # Let op: Dit is een basis implementatie, aanpassen naar echte SDK protocol
            return {"status": "ok", "message": "Command sent"}
            
        except socket.timeout:
            raise Go2TimeoutError("Timeout bij versturen commando")
        except Exception as e:
            raise Go2CommandError(f"Fout bij versturen commando: {e}")
    
    def stand(self):
        """Laat robot rechtop staan"""
        command = {
            "command": "stand",
            "mode": "stand"
        }
        return self.send_command(command)
    
    def sit(self):
        """Laat robot zitten"""
        command = {
            "command": "sit",
            "mode": "sit"
        }
        return self.send_command(command)
    
    def move(self, vx: float = 0.0, vy: float = 0.0, vyaw: float = 0.0):
        """
        Beweeg robot
        
        Args:
            vx: Snelheid vooruit/achteruit (m/s)
            vy: Snelheid links/rechts (m/s)
            vyaw: Draaisnelheid (rad/s)
        """
        command = {
            "command": "move",
            "vx": vx,
            "vy": vy,
            "vyaw": vyaw
        }
        return self.send_command(command)
    
    def stop(self):
        """Stop alle beweging"""
        return self.move(0.0, 0.0, 0.0)
    
    def get_state(self) -> Dict[str, Any]:
        """
        Haal robot status op
        
        Returns:
            Dictionary met robot status informatie
        """
        command = {
            "command": "get_state"
        }
        return self.send_command(command)
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

