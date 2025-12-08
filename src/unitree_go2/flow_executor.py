"""
Flow Executor voor Go2 Robot

Voert geautomatiseerde actiesequenties (flows) uit.
"""

import time
import math
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import yaml

from .robot import Go2Robot
from .exceptions import Go2CommandError


class ActionType(Enum):
    """Types van acties die uitgevoerd kunnen worden"""
    STAND = "stand"
    SIT = "sit"
    CROUCH = "crouch"  # Hurken
    MOVE = "move"
    MOVE_TO = "move_to"  # Naar specifieke positie
    ROTATE = "rotate"
    STOP = "stop"
    WAIT = "wait"
    SPEAK = "speak"
    VOICE_SPEAK = "voice_speak"  # Via voice controller
    CONDITION = "condition"  # Conditionele actie
    LOOP = "loop"  # Herhaal acties
    PARALLEL = "parallel"  # Voer acties parallel uit


@dataclass
class FlowAction:
    """Een enkele actie in een flow"""
    type: ActionType
    params: Dict[str, Any]
    name: Optional[str] = None
    duration: Optional[float] = None  # Duur in seconden
    condition: Optional[str] = None  # Python expressie voor conditionele uitvoering


class FlowExecutor:
    """
    Voert flows uit op de Go2 robot
    
    Een flow is een reeks acties die sequentieel of parallel worden uitgevoerd.
    """
    
    def __init__(self, robot: Go2Robot, voice_controller=None):
        """
        Initialiseer flow executor
        
        Args:
            robot: Go2Robot instantie
            voice_controller: Optionele voice controller voor spraak acties
        """
        self.robot = robot
        self.voice_controller = voice_controller
        self.is_running = False
        self.current_action: Optional[str] = None
        self.on_action_start: Optional[Callable] = None
        self.on_action_end: Optional[Callable] = None
        self.on_flow_complete: Optional[Callable] = None
        
        # State tracking voor beweging
        self.current_position = [0.0, 0.0, 0.0]  # x, y, yaw
        self.current_orientation = 0.0  # yaw angle
    
    def execute_action(self, action: FlowAction) -> bool:
        """
        Voer een enkele actie uit
        
        Args:
            action: De actie om uit te voeren
            
        Returns:
            True als actie succesvol was
        """
        if action.name:
            self.current_action = action.name
            if self.on_action_start:
                self.on_action_start(action.name)
        
        try:
            if action.type == ActionType.STAND:
                self.robot.stand()
                if action.duration:
                    time.sleep(action.duration)
                else:
                    time.sleep(1.0)  # Default tijd om te stabiliseren
                    
            elif action.type == ActionType.SIT:
                self.robot.sit()
                if action.duration:
                    time.sleep(action.duration)
                else:
                    time.sleep(1.0)
                    
            elif action.type == ActionType.CROUCH:
                # Hurken: tussen stand en sit
                # Gebruik custom joint positions of beweging
                # Voor nu: ga laag zitten
                self._crouch(action.params.get("height", 0.3))
                if action.duration:
                    time.sleep(action.duration)
                else:
                    time.sleep(1.0)
                    
            elif action.type == ActionType.MOVE:
                vx = action.params.get("vx", 0.0)
                vy = action.params.get("vy", 0.0)
                vyaw = action.params.get("vyaw", 0.0)
                duration = action.duration or action.params.get("duration", 1.0)
                
                self.robot.move(vx, vy, vyaw)
                time.sleep(duration)
                self.robot.stop()
                
                # Update positie (simpele schatting)
                self.current_position[0] += vx * duration * math.cos(self.current_orientation)
                self.current_position[1] += vx * duration * math.sin(self.current_orientation)
                self.current_orientation += vyaw * duration
                
            elif action.type == ActionType.MOVE_TO:
                # Beweeg naar specifieke positie
                target_x = action.params.get("x", 0.0)
                target_y = action.params.get("y", 0.0)
                target_yaw = action.params.get("yaw", None)
                speed = action.params.get("speed", 0.3)
                
                self._move_to_position(target_x, target_y, target_yaw, speed)
                
            elif action.type == ActionType.ROTATE:
                angle = action.params.get("angle", 0.0)  # In graden
                speed = action.params.get("speed", 0.5)  # rad/s
                
                # Converteer naar rad
                angle_rad = math.radians(angle)
                duration = abs(angle_rad / speed)
                
                vyaw = speed if angle_rad > 0 else -speed
                self.robot.move(0.0, 0.0, vyaw)
                time.sleep(duration)
                self.robot.stop()
                
                self.current_orientation += angle_rad
                
            elif action.type == ActionType.STOP:
                self.robot.stop()
                if action.duration:
                    time.sleep(action.duration)
                    
            elif action.type == ActionType.WAIT:
                duration = action.duration or action.params.get("duration", 1.0)
                time.sleep(duration)
                
            elif action.type == ActionType.SPEAK:
                text = action.params.get("text", "")
                print(f"🤖 Robot zegt: {text}")
                # Als voice controller beschikbaar is, gebruik die
                if self.voice_controller:
                    self.voice_controller.speak(text)
                else:
                    # Fallback: print alleen
                    print(f"💬 {text}")
                    
            elif action.type == ActionType.VOICE_SPEAK:
                text = action.params.get("text", "")
                if self.voice_controller:
                    self.voice_controller.speak(text)
                else:
                    print(f"⚠️  Voice controller niet beschikbaar: {text}")
                    
            elif action.type == ActionType.CONDITION:
                # Conditionele actie
                condition_expr = action.condition or action.params.get("condition", "True")
                if eval(condition_expr):
                    # Voer sub-acties uit
                    sub_actions = action.params.get("actions", [])
                    for sub_action_dict in sub_actions:
                        sub_action = self._dict_to_action(sub_action_dict)
                        self.execute_action(sub_action)
                        
            elif action.type == ActionType.LOOP:
                count = action.params.get("count", 1)
                actions = action.params.get("actions", [])
                
                for i in range(count):
                    for action_dict in actions:
                        sub_action = self._dict_to_action(action_dict)
                        self.execute_action(sub_action)
                        
            elif action.type == ActionType.PARALLEL:
                # Voer acties parallel uit (threading)
                import threading
                actions = action.params.get("actions", [])
                threads = []
                
                for action_dict in actions:
                    sub_action = self._dict_to_action(action_dict)
                    thread = threading.Thread(target=self.execute_action, args=(sub_action,))
                    thread.start()
                    threads.append(thread)
                
                # Wacht tot alle threads klaar zijn
                for thread in threads:
                    thread.join()
            
            if action.name and self.on_action_end:
                self.on_action_end(action.name)
                
            return True
            
        except Exception as e:
            print(f"❌ Fout bij uitvoeren actie {action.name or action.type.value}: {e}")
            return False
    
    def _crouch(self, height: float = 0.3):
        """
        Laat robot hurken
        
        Args:
            height: Hoogte factor (0.0 = volledig zitten, 1.0 = volledig staan)
        """
        # Voor nu: gebruik sit met aangepaste timing
        # In echte implementatie: custom joint positions
        if height < 0.5:
            self.robot.sit()
        else:
            # Tussenstand: eerst laag gaan, dan iets omhoog
            self.robot.sit()
            time.sleep(0.5)
            # Custom: zou joint positions moeten aanpassen
            # Voor nu: blijf laag zitten
            pass
    
    def _move_to_position(self, target_x: float, target_y: float, target_yaw: Optional[float], speed: float):
        """
        Beweeg naar specifieke positie
        
        Args:
            target_x: Doel x positie (meter)
            target_y: Doel y positie (meter)
            target_yaw: Doel orientatie (rad, optioneel)
            speed: Bewegingssnelheid (m/s)
        """
        # Bereken afstand en richting
        dx = target_x - self.current_position[0]
        dy = target_y - self.current_position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 0.1:  # Dichtbij genoeg
            # Alleen rotatie indien nodig
            if target_yaw is not None:
                angle_diff = target_yaw - self.current_orientation
                if abs(angle_diff) > 0.1:
                    self.robot.move(0.0, 0.0, math.copysign(0.5, angle_diff))
                    time.sleep(abs(angle_diff) / 0.5)
                    self.robot.stop()
            return
        
        # Bereken richting
        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - self.current_orientation
        
        # Rotate naar doel
        if abs(angle_diff) > 0.2:
            self.robot.move(0.0, 0.0, math.copysign(0.5, angle_diff))
            time.sleep(abs(angle_diff) / 0.5)
            self.robot.stop()
            self.current_orientation = target_angle
        
        # Beweeg vooruit
        duration = distance / speed
        self.robot.move(speed, 0.0, 0.0)
        time.sleep(duration)
        self.robot.stop()
        
        # Update positie
        self.current_position[0] = target_x
        self.current_position[1] = target_y
        
        # Finale rotatie indien nodig
        if target_yaw is not None:
            angle_diff = target_yaw - self.current_orientation
            if abs(angle_diff) > 0.1:
                self.robot.move(0.0, 0.0, math.copysign(0.5, angle_diff))
                time.sleep(abs(angle_diff) / 0.5)
                self.robot.stop()
                self.current_orientation = target_yaw
    
    def _dict_to_action(self, action_dict: Dict[str, Any]) -> FlowAction:
        """Converteer dictionary naar FlowAction"""
        action_type_str = action_dict.get("type", "")
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            raise ValueError(f"Onbekend actie type: {action_type_str}")
        
        return FlowAction(
            type=action_type,
            params=action_dict.get("params", {}),
            name=action_dict.get("name"),
            duration=action_dict.get("duration"),
            condition=action_dict.get("condition")
        )
    
    def execute_flow(self, actions: List[Dict[str, Any]], stop_on_error: bool = True) -> bool:
        """
        Voer een flow uit
        
        Args:
            actions: Lijst van actie dictionaries
            stop_on_error: Stop bij eerste fout
            
        Returns:
            True als flow succesvol was
        """
        self.is_running = True
        
        try:
            for i, action_dict in enumerate(actions):
                if not self.is_running:
                    print("⚠️  Flow gestopt door gebruiker")
                    break
                
                action = self._dict_to_action(action_dict)
                
                # Check condition
                if action.condition:
                    try:
                        if not eval(action.condition):
                            print(f"⏭️  Actie {action.name or i} overgeslagen (condition false)")
                            continue
                    except Exception as e:
                        print(f"⚠️  Fout bij evalueren condition: {e}")
                        if stop_on_error:
                            return False
                        continue
                
                print(f"▶️  Uitvoeren: {action.name or action.type.value}")
                
                success = self.execute_action(action)
                
                if not success and stop_on_error:
                    print(f"❌ Flow gestopt bij actie {action.name or i}")
                    return False
            
            if self.on_flow_complete:
                self.on_flow_complete()
            
            print("✓ Flow voltooid")
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️  Flow onderbroken door gebruiker")
            self.robot.stop()
            return False
        except Exception as e:
            print(f"❌ Fout in flow: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.is_running = False
            self.current_action = None
    
    def stop(self):
        """Stop huidige flow"""
        self.is_running = False
        self.robot.stop()
    
    def load_flow_from_yaml(self, yaml_path: str) -> List[Dict[str, Any]]:
        """
        Laad flow uit YAML bestand
        
        Args:
            yaml_path: Pad naar YAML bestand
            
        Returns:
            Lijst van actie dictionaries
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return data.get("actions", [])


def create_welcome_flow(distance: float = 2.0) -> List[Dict[str, Any]]:
    """
    Maak een welkom flow: loop naar persoon, hurk, en heet welkom
    
    Args:
        distance: Afstand om te lopen (meter)
        
    Returns:
        Flow acties
    """
    return [
        {
            "name": "Sta op",
            "type": "stand",
            "duration": 2.0
        },
        {
            "name": "Loop naar persoon",
            "type": "move",
            "params": {
                "vx": 0.3,
                "vy": 0.0,
                "vyaw": 0.0
            },
            "duration": distance / 0.3  # Bereken duur op basis van afstand
        },
        {
            "name": "Stop",
            "type": "stop",
            "duration": 0.5
        },
        {
            "name": "Hurk",
            "type": "crouch",
            "params": {
                "height": 0.4
            },
            "duration": 2.0
        },
        {
            "name": "Welkom heten",
            "type": "voice_speak",
            "params": {
                "text": "Welkom! Leuk je te zien!"
            }
        },
        {
            "name": "Wacht even",
            "type": "wait",
            "duration": 2.0
        },
        {
            "name": "Sta weer op",
            "type": "stand",
            "duration": 2.0
        }
    ]

