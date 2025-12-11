"""
Unitree Go2 EDU Robot Interface

Wrapper rondom de officiële unitree_sdk2_python SDK.
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
except ImportError as e:
    HAS_OFFICIAL_SDK = False
    _import_error = str(e)

from .exceptions import Go2ConnectionError, Go2CommandError, Go2TimeoutError


class Go2Robot:
    """
    Hoofdklasse voor interactie met Unitree Go2 EDU robot.
    
    Gebruikt de officiële unitree_sdk2_python SDK voor communicatie.
    Ondersteunt alle high-level sport commando's van de officiële SDK.
    """
    
    def __init__(self, ip_address: str = "192.168.123.161", timeout: float = 5.0, network_interface: Optional[str] = None):
        """
        Initialiseer Go2 robot verbinding
        
        Args:
            ip_address: IP adres van de robot
            timeout: Timeout in seconden
            network_interface: Netwerk interface naam (bijv. "en0", "eth0")
                              Als None, wordt automatisch gedetecteerd
        """
        if not HAS_OFFICIAL_SDK:
            raise ImportError(
                f"Officiële SDK niet gevonden. Installeer CycloneDDS en unitree_sdk2_python.\n"
                f"Zie docs/OFFICIELE_SDK_INTEGRATIE.md voor instructies.\n"
                f"Fout: {_import_error if '_import_error' in dir() else 'Unknown'}"
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
    
    def _check_connection(self):
        """Check of verbonden met robot"""
        if not self.connected:
            raise Go2ConnectionError("Niet verbonden met robot")
    
    def _execute_command(self, command_func, command_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Voer een SDK commando uit met error handling
        
        Args:
            command_func: De SDK functie om uit te voeren
            command_name: Naam van het commando voor foutmeldingen
            *args, **kwargs: Argumenten voor de functie
            
        Returns:
            Dictionary met status en resultaat
        """
        self._check_connection()
        try:
            result = command_func(*args, **kwargs)
            # Sommige functies retourneren een tuple (code, data)
            if isinstance(result, tuple):
                code, data = result
                if code != 0:
                    raise Go2CommandError(f"{command_name} mislukt met code: {code}")
                return {"status": "ok", "message": f"{command_name} sent", "code": code, "data": data}
            else:
                code = result
                if code != 0:
                    raise Go2CommandError(f"{command_name} mislukt met code: {code}")
                return {"status": "ok", "message": f"{command_name} sent", "code": code}
        except Go2CommandError:
            raise
        except Exception as e:
            raise Go2CommandError(f"Fout bij {command_name}: {e}")

    # ==================== BASIS BEWEGING ====================
    
    def stand(self):
        """Laat robot rechtop staan"""
        return self._execute_command(self.sport_client.StandUp, "StandUp")
    
    def sit(self):
        """Laat robot zitten (StandDown)"""
        return self._execute_command(self.sport_client.StandDown, "StandDown")
    
    def stand_down(self):
        """Laat robot naar beneden gaan (liggen)"""
        return self._execute_command(self.sport_client.StandDown, "StandDown")
    
    def move(self, vx: float = 0.0, vy: float = 0.0, vyaw: float = 0.0):
        """
        Beweeg robot met opgegeven snelheden
        
        Args:
            vx: Snelheid vooruit/achteruit (m/s)
            vy: Snelheid links/rechts (m/s)
            vyaw: Draaisnelheid (rad/s)
        """
        return self._execute_command(self.sport_client.Move, "Move", vx, vy, vyaw)
    
    def stop(self):
        """Stop alle beweging"""
        return self._execute_command(self.sport_client.StopMove, "StopMove")
    
    def damp(self):
        """Zet robot in damp mode (motoren uit, robot zakt in)"""
        return self._execute_command(self.sport_client.Damp, "Damp")
    
    def balance_stand(self):
        """Gebalanceerd staan (actieve balans)"""
        return self._execute_command(self.sport_client.BalanceStand, "BalanceStand")
    
    def recovery_stand(self):
        """Herstel naar staande positie (na val)"""
        return self._execute_command(self.sport_client.RecoveryStand, "RecoveryStand")

    # ==================== POSES & TRICKS ====================
    
    def sit_down(self):
        """Ga zitten (echte zit positie)"""
        return self._execute_command(self.sport_client.Sit, "Sit")
    
    def rise_sit(self):
        """Sta op vanuit zit positie"""
        return self._execute_command(self.sport_client.RiseSit, "RiseSit")
    
    def hello(self):
        """Zwaai/groet beweging"""
        return self._execute_command(self.sport_client.Hello, "Hello")
    
    def stretch(self):
        """Rek beweging"""
        return self._execute_command(self.sport_client.Stretch, "Stretch")
    
    def heart(self):
        """Hart gebaar maken"""
        return self._execute_command(self.sport_client.Heart, "Heart")
    
    def scrape(self):
        """Krab beweging"""
        return self._execute_command(self.sport_client.Scrape, "Scrape")
    
    def content(self):
        """Tevreden/blij beweging"""
        return self._execute_command(self.sport_client.Content, "Content")
    
    def pose(self, enabled: bool = True):
        """
        Pose modus aan/uit
        
        Args:
            enabled: True om pose modus aan te zetten
        """
        return self._execute_command(self.sport_client.Pose, "Pose", enabled)

    # ==================== DANSEN ====================
    
    def dance1(self):
        """Dans routine 1"""
        return self._execute_command(self.sport_client.Dance1, "Dance1")
    
    def dance2(self):
        """Dans routine 2"""
        return self._execute_command(self.sport_client.Dance2, "Dance2")

    # ==================== ACROBATIEK ====================
    
    def front_flip(self):
        """Salto voorwaarts (⚠️ GEVAARLIJK - zorg voor ruimte!)"""
        return self._execute_command(self.sport_client.FrontFlip, "FrontFlip")
    
    def back_flip(self):
        """Salto achterwaarts (⚠️ GEVAARLIJK - zorg voor ruimte!)"""
        return self._execute_command(self.sport_client.BackFlip, "BackFlip")
    
    def left_flip(self):
        """Salto naar links (⚠️ GEVAARLIJK - zorg voor ruimte!)"""
        return self._execute_command(self.sport_client.LeftFlip, "LeftFlip")
    
    def front_jump(self):
        """Spring voorwaarts"""
        return self._execute_command(self.sport_client.FrontJump, "FrontJump")
    
    def front_pounce(self):
        """Spring/duik voorwaarts"""
        return self._execute_command(self.sport_client.FrontPounce, "FrontPounce")
    
    def hand_stand(self, enabled: bool = True):
        """
        Handstand positie
        
        Args:
            enabled: True om handstand te starten, False om te stoppen
        """
        return self._execute_command(self.sport_client.HandStand, "HandStand", enabled)

    # ==================== LOOPSTIJLEN ====================
    
    def free_walk(self):
        """Vrije loop modus"""
        return self._execute_command(self.sport_client.FreeWalk, "FreeWalk")
    
    def static_walk(self):
        """Statische loop (langzaam, stabiel)"""
        return self._execute_command(self.sport_client.StaticWalk, "StaticWalk")
    
    def trot_run(self):
        """Draf/ren modus"""
        return self._execute_command(self.sport_client.TrotRun, "TrotRun")
    
    def classic_walk(self, enabled: bool = True):
        """
        Klassieke loop stijl
        
        Args:
            enabled: True om aan te zetten, False om uit te zetten
        """
        return self._execute_command(self.sport_client.ClassicWalk, "ClassicWalk", enabled)
    
    def walk_upright(self, enabled: bool = True):
        """
        Rechtop lopen (op twee poten)
        
        Args:
            enabled: True om aan te zetten, False om uit te zetten
        """
        return self._execute_command(self.sport_client.WalkUpright, "WalkUpright", enabled)
    
    def cross_step(self, enabled: bool = True):
        """
        Kruis-stap beweging
        
        Args:
            enabled: True om aan te zetten, False om uit te zetten
        """
        return self._execute_command(self.sport_client.CrossStep, "CrossStep", enabled)

    # ==================== SPECIALE MODI ====================
    
    def free_bound(self, enabled: bool = True):
        """
        Vrij springen/bonden modus
        
        Args:
            enabled: True om aan te zetten, False om uit te zetten
        """
        return self._execute_command(self.sport_client.FreeBound, "FreeBound", enabled)
    
    def free_jump(self, enabled: bool = True):
        """
        Vrij springen modus
        
        Args:
            enabled: True om aan te zetten, False om uit te zetten
        """
        return self._execute_command(self.sport_client.FreeJump, "FreeJump", enabled)
    
    def free_avoid(self, enabled: bool = True):
        """
        Vrij ontwijken modus (obstakel vermijding)
        
        Args:
            enabled: True om aan te zetten, False om uit te zetten
        """
        return self._execute_command(self.sport_client.FreeAvoid, "FreeAvoid", enabled)

    # ==================== INSTELLINGEN ====================
    
    def set_speed_level(self, level: int):
        """
        Stel snelheidsniveau in
        
        Args:
            level: Snelheidsniveau (0-2, waarbij 0=langzaam, 2=snel)
        """
        return self._execute_command(self.sport_client.SpeedLevel, "SpeedLevel", level)
    
    def set_euler(self, roll: float, pitch: float, yaw: float):
        """
        Stel lichaam oriëntatie in (Euler hoeken)
        
        Args:
            roll: Rol hoek (rad)
            pitch: Pitch hoek (rad)
            yaw: Yaw hoek (rad)
        """
        return self._execute_command(self.sport_client.Euler, "Euler", roll, pitch, yaw)
    
    def switch_joystick(self, enabled: bool):
        """
        Schakel joystick controle in/uit
        
        Args:
            enabled: True om joystick aan te zetten
        """
        return self._execute_command(self.sport_client.SwitchJoystick, "SwitchJoystick", enabled)
    
    def set_auto_recovery(self, enabled: bool):
        """
        Stel automatisch herstel in/uit
        
        Args:
            enabled: True om automatisch herstel aan te zetten
        """
        return self._execute_command(self.sport_client.AutoRecoverySet, "AutoRecoverySet", enabled)
    
    def get_auto_recovery(self) -> bool:
        """
        Haal automatisch herstel status op
        
        Returns:
            True als automatisch herstel aan staat
        """
        result = self._execute_command(self.sport_client.AutoRecoveryGet, "AutoRecoveryGet")
        return result.get("data", False)
    
    def switch_avoid_mode(self):
        """Wissel obstakel vermijding modus"""
        return self._execute_command(self.sport_client.SwitchAvoidMode, "SwitchAvoidMode")

    # ==================== STATUS ====================
    
    def get_state(self) -> Dict[str, Any]:
        """
        Haal robot status op
        
        Returns:
            Dictionary met robot status informatie
            
        Note: Officiële SDK gebruikt subscription model voor state.
        Deze implementatie is een vereenvoudigde versie.
        """
        self._check_connection()
        
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
