"""
Flow Executor voor Go2 Robot

Voert geautomatiseerde actiesequenties (flows) uit.
Ondersteunt alle officiële SDK commando's.
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
    # Basis beweging
    STAND = "stand"
    SIT = "sit"
    STAND_DOWN = "stand_down"
    MOVE = "move"
    MOVE_TO = "move_to"
    ROTATE = "rotate"
    STOP = "stop"
    DAMP = "damp"
    BALANCE_STAND = "balance_stand"
    RECOVERY_STAND = "recovery_stand"
    
    # Poses & Tricks
    SIT_DOWN = "sit_down"
    RISE_SIT = "rise_sit"
    HELLO = "hello"
    STRETCH = "stretch"
    HEART = "heart"
    SCRAPE = "scrape"
    CONTENT = "content"
    POSE = "pose"
    
    # Dansen
    DANCE1 = "dance1"
    DANCE2 = "dance2"
    
    # Acrobatiek
    FRONT_FLIP = "front_flip"
    BACK_FLIP = "back_flip"
    LEFT_FLIP = "left_flip"
    FRONT_JUMP = "front_jump"
    FRONT_POUNCE = "front_pounce"
    HAND_STAND = "hand_stand"
    
    # Loopstijlen
    FREE_WALK = "free_walk"
    STATIC_WALK = "static_walk"
    TROT_RUN = "trot_run"
    CLASSIC_WALK = "classic_walk"
    WALK_UPRIGHT = "walk_upright"
    CROSS_STEP = "cross_step"
    
    # Speciale modi
    FREE_BOUND = "free_bound"
    FREE_JUMP = "free_jump"
    FREE_AVOID = "free_avoid"
    
    # Instellingen
    SPEED_LEVEL = "speed_level"
    EULER = "euler"
    SWITCH_JOYSTICK = "switch_joystick"
    AUTO_RECOVERY = "auto_recovery"
    SWITCH_AVOID_MODE = "switch_avoid_mode"
    
    # Utility acties
    WAIT = "wait"
    SPEAK = "speak"
    VOICE_SPEAK = "voice_speak"
    WEB_SEARCH = "web_search"
    DISPLAY = "display"
    
    # Flow controle
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    
    # Legacy (voor backwards compatibiliteit)
    CROUCH = "crouch"


@dataclass
class FlowAction:
    """Een enkele actie in een flow"""
    type: ActionType
    params: Dict[str, Any]
    name: Optional[str] = None
    duration: Optional[float] = None
    condition: Optional[str] = None


class FlowExecutor:
    """
    Voert flows uit op de Go2 robot
    
    Een flow is een reeks acties die sequentieel of parallel worden uitgevoerd.
    Ondersteunt alle officiële SDK commando's.
    """
    
    def __init__(self, robot: Go2Robot, voice_controller=None, 
                 web_searcher=None, display_api_url: Optional[str] = None):
        """
        Initialiseer flow executor
        
        Args:
            robot: Go2Robot instantie
            voice_controller: Optionele voice controller voor spraak acties
            web_searcher: Optionele web searcher voor zoek acties
            display_api_url: Optionele URL voor display API
        """
        self.robot = robot
        self.voice_controller = voice_controller
        self.web_searcher = web_searcher
        self.display_api_url = display_api_url
        
        self.is_running = False
        self.current_action: Optional[str] = None
        self.on_action_start: Optional[Callable] = None
        self.on_action_end: Optional[Callable] = None
        self.on_flow_complete: Optional[Callable] = None
        
        # State tracking voor beweging
        self.current_position = [0.0, 0.0, 0.0]
        self.current_orientation = 0.0
    
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
            success = self._execute_action_impl(action)
            
            if action.name and self.on_action_end:
                self.on_action_end(action.name)
                
            return success
            
        except Exception as e:
            print(f"❌ Fout bij uitvoeren actie {action.name or action.type.value}: {e}")
            return False
    
    def _execute_action_impl(self, action: FlowAction) -> bool:
        """Interne implementatie van actie uitvoering"""
        
        # ==================== BASIS BEWEGING ====================
        
        if action.type == ActionType.STAND:
            self.robot.stand()
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.SIT:
            self.robot.sit()
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.STAND_DOWN:
            self.robot.stand_down()
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.MOVE:
            vx = action.params.get("vx", 0.0)
            vy = action.params.get("vy", 0.0)
            vyaw = action.params.get("vyaw", 0.0)
            duration = action.duration or action.params.get("duration", 1.0)
            
            self.robot.move(vx, vy, vyaw)
            time.sleep(duration)
            self.robot.stop()
            
            # Update positie schatting
            self.current_position[0] += vx * duration * math.cos(self.current_orientation)
            self.current_position[1] += vx * duration * math.sin(self.current_orientation)
            self.current_orientation += vyaw * duration
            
        elif action.type == ActionType.MOVE_TO:
            target_x = action.params.get("x", 0.0)
            target_y = action.params.get("y", 0.0)
            target_yaw = action.params.get("yaw", None)
            speed = action.params.get("speed", 0.3)
            self._move_to_position(target_x, target_y, target_yaw, speed)
            
        elif action.type == ActionType.ROTATE:
            angle = action.params.get("angle", 0.0)
            speed = action.params.get("speed", 0.5)
            
            angle_rad = math.radians(angle)
            duration = abs(angle_rad / speed)
            
            vyaw = speed if angle_rad > 0 else -speed
            self.robot.move(0.0, 0.0, vyaw)
            time.sleep(duration)
            self.robot.stop()
            
            self.current_orientation += angle_rad
            
        elif action.type == ActionType.STOP:
            self.robot.stop()
            self._wait_duration(action)
            
        elif action.type == ActionType.DAMP:
            self.robot.damp()
            self._wait_duration(action, default=0.5)
            
        elif action.type == ActionType.BALANCE_STAND:
            self.robot.balance_stand()
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.RECOVERY_STAND:
            self.robot.recovery_stand()
            self._wait_duration(action, default=2.0)
        
        # ==================== POSES & TRICKS ====================
        
        elif action.type == ActionType.SIT_DOWN:
            self.robot.sit_down()
            self._wait_duration(action, default=2.0)
            
        elif action.type == ActionType.RISE_SIT:
            self.robot.rise_sit()
            self._wait_duration(action, default=2.0)
            
        elif action.type == ActionType.HELLO:
            self.robot.hello()
            self._wait_duration(action, default=3.0)
            
        elif action.type == ActionType.STRETCH:
            self.robot.stretch()
            self._wait_duration(action, default=3.0)
            
        elif action.type == ActionType.HEART:
            self.robot.heart()
            self._wait_duration(action, default=3.0)
            
        elif action.type == ActionType.SCRAPE:
            self.robot.scrape()
            self._wait_duration(action, default=2.0)
            
        elif action.type == ActionType.CONTENT:
            self.robot.content()
            self._wait_duration(action, default=2.0)
            
        elif action.type == ActionType.POSE:
            enabled = action.params.get("enabled", True)
            self.robot.pose(enabled)
            self._wait_duration(action, default=1.0)
        
        # ==================== DANSEN ====================
        
        elif action.type == ActionType.DANCE1:
            self.robot.dance1()
            self._wait_duration(action, default=10.0)
            
        elif action.type == ActionType.DANCE2:
            self.robot.dance2()
            self._wait_duration(action, default=10.0)
        
        # ==================== ACROBATIEK ====================
        
        elif action.type == ActionType.FRONT_FLIP:
            print("⚠️  WAARSCHUWING: Front flip - zorg voor voldoende ruimte!")
            self.robot.front_flip()
            self._wait_duration(action, default=3.0)
            
        elif action.type == ActionType.BACK_FLIP:
            print("⚠️  WAARSCHUWING: Back flip - zorg voor voldoende ruimte!")
            self.robot.back_flip()
            self._wait_duration(action, default=3.0)
            
        elif action.type == ActionType.LEFT_FLIP:
            print("⚠️  WAARSCHUWING: Left flip - zorg voor voldoende ruimte!")
            self.robot.left_flip()
            self._wait_duration(action, default=3.0)
            
        elif action.type == ActionType.FRONT_JUMP:
            self.robot.front_jump()
            self._wait_duration(action, default=2.0)
            
        elif action.type == ActionType.FRONT_POUNCE:
            self.robot.front_pounce()
            self._wait_duration(action, default=2.0)
            
        elif action.type == ActionType.HAND_STAND:
            enabled = action.params.get("enabled", True)
            self.robot.hand_stand(enabled)
            duration = action.duration or action.params.get("duration", 4.0)
            if enabled:
                time.sleep(duration)
                self.robot.hand_stand(False)
        
        # ==================== LOOPSTIJLEN ====================
        
        elif action.type == ActionType.FREE_WALK:
            self.robot.free_walk()
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.STATIC_WALK:
            self.robot.static_walk()
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.TROT_RUN:
            self.robot.trot_run()
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.CLASSIC_WALK:
            enabled = action.params.get("enabled", True)
            self.robot.classic_walk(enabled)
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.WALK_UPRIGHT:
            enabled = action.params.get("enabled", True)
            self.robot.walk_upright(enabled)
            duration = action.duration or action.params.get("duration", 4.0)
            if enabled:
                time.sleep(duration)
                self.robot.walk_upright(False)
            
        elif action.type == ActionType.CROSS_STEP:
            enabled = action.params.get("enabled", True)
            self.robot.cross_step(enabled)
            duration = action.duration or action.params.get("duration", 4.0)
            if enabled:
                time.sleep(duration)
                self.robot.cross_step(False)
        
        # ==================== SPECIALE MODI ====================
        
        elif action.type == ActionType.FREE_BOUND:
            enabled = action.params.get("enabled", True)
            self.robot.free_bound(enabled)
            duration = action.duration or action.params.get("duration", 2.0)
            if enabled:
                time.sleep(duration)
                self.robot.free_bound(False)
            
        elif action.type == ActionType.FREE_JUMP:
            enabled = action.params.get("enabled", True)
            self.robot.free_jump(enabled)
            duration = action.duration or action.params.get("duration", 4.0)
            if enabled:
                time.sleep(duration)
                self.robot.free_jump(False)
            
        elif action.type == ActionType.FREE_AVOID:
            enabled = action.params.get("enabled", True)
            self.robot.free_avoid(enabled)
            duration = action.duration or action.params.get("duration", 2.0)
            if enabled:
                time.sleep(duration)
                self.robot.free_avoid(False)
        
        # ==================== INSTELLINGEN ====================
        
        elif action.type == ActionType.SPEED_LEVEL:
            level = action.params.get("level", 1)
            self.robot.set_speed_level(level)
            
        elif action.type == ActionType.EULER:
            roll = action.params.get("roll", 0.0)
            pitch = action.params.get("pitch", 0.0)
            yaw = action.params.get("yaw", 0.0)
            self.robot.set_euler(roll, pitch, yaw)
            self._wait_duration(action, default=1.0)
            
        elif action.type == ActionType.SWITCH_JOYSTICK:
            enabled = action.params.get("enabled", True)
            self.robot.switch_joystick(enabled)
            
        elif action.type == ActionType.AUTO_RECOVERY:
            enabled = action.params.get("enabled", True)
            self.robot.set_auto_recovery(enabled)
            
        elif action.type == ActionType.SWITCH_AVOID_MODE:
            self.robot.switch_avoid_mode()
        
        # ==================== UTILITY ACTIES ====================
        
        elif action.type == ActionType.WAIT:
            duration = action.duration or action.params.get("duration", 1.0)
            time.sleep(duration)
            
        elif action.type == ActionType.SPEAK:
            text = action.params.get("text", "")
            print(f"🤖 Robot zegt: {text}")
            if self.voice_controller:
                self.voice_controller.speak(text)
            else:
                print(f"💬 {text}")
                
        elif action.type == ActionType.VOICE_SPEAK:
            text = action.params.get("text", "")
            if self.voice_controller:
                self.voice_controller.speak(text)
            else:
                print(f"⚠️  Voice controller niet beschikbaar: {text}")
                
        elif action.type == ActionType.WEB_SEARCH:
            self._execute_web_search(action)
            
        elif action.type == ActionType.DISPLAY:
            self._execute_display(action)
        
        # ==================== FLOW CONTROLE ====================
        
        elif action.type == ActionType.CONDITION:
            condition_expr = action.condition or action.params.get("condition", "True")
            if eval(condition_expr):
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
            import threading
            actions = action.params.get("actions", [])
            threads = []
            
            for action_dict in actions:
                sub_action = self._dict_to_action(action_dict)
                thread = threading.Thread(target=self.execute_action, args=(sub_action,))
                thread.start()
                threads.append(thread)
            
            for thread in threads:
                thread.join()
        
        # ==================== LEGACY ====================
        
        elif action.type == ActionType.CROUCH:
            # Backwards compatibiliteit: crouch = sit
            self.robot.sit()
            self._wait_duration(action, default=1.0)
        
        else:
            print(f"⚠️  Onbekend actie type: {action.type}")
            return False
        
        return True
    
    def _wait_duration(self, action: FlowAction, default: float = 0.0):
        """Wacht de opgegeven duration of default tijd"""
        duration = action.duration or action.params.get("duration", default)
        if duration > 0:
            time.sleep(duration)
    
    def _move_to_position(self, target_x: float, target_y: float, 
                          target_yaw: Optional[float], speed: float):
        """Beweeg naar specifieke positie"""
        dx = target_x - self.current_position[0]
        dy = target_y - self.current_position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 0.1:
            if target_yaw is not None:
                angle_diff = target_yaw - self.current_orientation
                if abs(angle_diff) > 0.1:
                    self.robot.move(0.0, 0.0, math.copysign(0.5, angle_diff))
                    time.sleep(abs(angle_diff) / 0.5)
                    self.robot.stop()
            return
        
        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - self.current_orientation
        
        if abs(angle_diff) > 0.2:
            self.robot.move(0.0, 0.0, math.copysign(0.5, angle_diff))
            time.sleep(abs(angle_diff) / 0.5)
            self.robot.stop()
            self.current_orientation = target_angle
        
        duration = distance / speed
        self.robot.move(speed, 0.0, 0.0)
        time.sleep(duration)
        self.robot.stop()
        
        self.current_position[0] = target_x
        self.current_position[1] = target_y
        
        if target_yaw is not None:
            angle_diff = target_yaw - self.current_orientation
            if abs(angle_diff) > 0.1:
                self.robot.move(0.0, 0.0, math.copysign(0.5, angle_diff))
                time.sleep(abs(angle_diff) / 0.5)
                self.robot.stop()
                self.current_orientation = target_yaw
    
    def _execute_web_search(self, action: FlowAction):
        """Voer web search actie uit"""
        query = action.params.get("query", "")
        max_results = action.params.get("max_results", 5)
        
        if not self.web_searcher:
            try:
                from .web_search import WebSearcher
                self.web_searcher = WebSearcher()
            except ImportError:
                print(f"⚠️  Web searcher niet beschikbaar")
                return
        
        print(f"🔍 Zoeken op internet: {query}")
        results = self.web_searcher.search(query, max_results)
        
        if action.params.get("speak_results", False) and self.voice_controller:
            summary = self.web_searcher.search_and_summarize(query, max_results=3)
            self.voice_controller.speak(summary)
        
        if action.params.get("show_on_display", True) and self.display_api_url:
            self._update_display_search(query, results)
        
        action.params["_search_results"] = results
    
    def _execute_display(self, action: FlowAction):
        """Voer display actie uit"""
        content = action.params.get("content", "")
        title = action.params.get("title", "Go2 Robot Display")
        display_type = action.params.get("display_type", "text")
        
        if self.display_api_url:
            self._update_display(title, content, display_type)
        else:
            print(f"📺 Display: {title} - {content}")
    
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
    
    def _update_display(self, title: str, content: str, display_type: str = "text"):
        """Update display via API"""
        if not self.display_api_url:
            return
        try:
            import requests
            requests.post(
                f"{self.display_api_url}/display",
                json={"title": title, "content": content, "type": display_type},
                timeout=2
            )
        except Exception as e:
            print(f"⚠️  Kon display niet updaten: {e}")
    
    def _update_display_search(self, query: str, results: List[Dict[str, Any]]):
        """Update display met zoekresultaten"""
        if not self.display_api_url:
            return
        try:
            import requests
            requests.post(
                f"{self.display_api_url}/display/search",
                json={"query": query, "results": results},
                timeout=2
            )
        except Exception as e:
            print(f"⚠️  Kon zoekresultaten niet tonen: {e}")
    
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


# ==================== PRESET FLOWS ====================

def create_welcome_flow(distance: float = 2.0) -> List[Dict[str, Any]]:
    """
    Maak een welkom flow: loop naar persoon, groet, en heet welkom
    
    Args:
        distance: Afstand om te lopen (meter)
        
    Returns:
        Flow acties
    """
    return [
        {"name": "Sta op", "type": "stand", "duration": 2.0},
        {"name": "Loop naar persoon", "type": "move",
         "params": {"vx": 0.3, "vy": 0.0, "vyaw": 0.0},
         "duration": distance / 0.3},
        {"name": "Stop", "type": "stop", "duration": 0.5},
        {"name": "Groet", "type": "hello", "duration": 3.0},
        {"name": "Welkom heten", "type": "voice_speak",
         "params": {"text": "Welkom! Leuk je te zien!"}},
        {"name": "Wacht even", "type": "wait", "duration": 2.0},
        {"name": "Sta weer op", "type": "stand", "duration": 2.0}
    ]


def create_dance_flow() -> List[Dict[str, Any]]:
    """
    Maak een dans flow
    
    Returns:
        Flow acties
    """
    return [
        {"name": "Sta op", "type": "stand", "duration": 2.0},
        {"name": "Aankondiging", "type": "voice_speak",
         "params": {"text": "Tijd om te dansen!"}},
        {"name": "Dans 1", "type": "dance1", "duration": 10.0},
        {"name": "Pauze", "type": "wait", "duration": 2.0},
        {"name": "Dans 2", "type": "dance2", "duration": 10.0},
        {"name": "Buiging", "type": "sit_down", "duration": 2.0},
        {"name": "Applaus", "type": "voice_speak",
         "params": {"text": "Dank je wel!"}},
        {"name": "Sta op", "type": "rise_sit", "duration": 2.0}
    ]


def create_tricks_flow() -> List[Dict[str, Any]]:
    """
    Maak een tricks demonstratie flow
    
    Returns:
        Flow acties
    """
    return [
        {"name": "Sta op", "type": "stand", "duration": 2.0},
        {"name": "Intro", "type": "voice_speak",
         "params": {"text": "Kijk wat ik kan!"}},
        {"name": "Zwaai", "type": "hello", "duration": 3.0},
        {"name": "Rek uit", "type": "stretch", "duration": 3.0},
        {"name": "Hart", "type": "heart", "duration": 3.0},
        {"name": "Tevreden", "type": "content", "duration": 2.0},
        {"name": "Einde", "type": "voice_speak",
         "params": {"text": "Dat was het! Tot de volgende keer!"}}
    ]


def create_acrobatics_flow() -> List[Dict[str, Any]]:
    """
    Maak een acrobatiek flow (⚠️ GEVAARLIJK - alleen met voldoende ruimte!)
    
    Returns:
        Flow acties
    """
    return [
        {"name": "Sta op", "type": "stand", "duration": 2.0},
        {"name": "Waarschuwing", "type": "voice_speak",
         "params": {"text": "Let op! Acrobatiek begint. Zorg voor voldoende ruimte!"}},
        {"name": "Wacht", "type": "wait", "duration": 3.0},
        {"name": "Spring vooruit", "type": "front_jump", "duration": 2.0},
        {"name": "Herstel", "type": "recovery_stand", "duration": 2.0},
        {"name": "Handstand", "type": "hand_stand", 
         "params": {"enabled": True}, "duration": 4.0},
        {"name": "Einde", "type": "voice_speak",
         "params": {"text": "Acrobatiek voltooid!"}}
    ]
