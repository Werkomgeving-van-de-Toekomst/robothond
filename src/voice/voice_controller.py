"""
Voice Control voor Unitree Go2 Robot

Spraakherkenning en commando interpretatie voor robot besturing.
"""

import sys
import os
from pathlib import Path
import json
import re
from typing import Optional, Dict, List, Callable, Any
import threading
import queue

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import speech_recognition as sr
    import pyttsx3
except ImportError:
    raise ImportError(
        "Voice dependencies niet geïnstalleerd. Installeer met: pip install SpeechRecognition pyttsx3"
    )

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class VoiceController:
    """
    Voice controller voor Go2 robot
    
    Luistert naar spraak commando's en voert acties uit.
    """
    
    def __init__(
        self,
        language: str = "nl-NL",
        use_openai: bool = False,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialiseer voice controller
        
        Args:
            language: Taal voor spraakherkenning (default: nl-NL)
            use_openai: Gebruik OpenAI Whisper voor betere herkenning
            openai_api_key: OpenAI API key (vereist als use_openai=True)
        """
        self.language = language
        self.use_openai = use_openai and HAS_OPENAI
        
        # Spraakherkenning
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Spreeksnelheid
        self.tts_engine.setProperty('volume', 0.9)
        
        # OpenAI setup
        if self.use_openai:
            if not openai_api_key:
                raise ValueError("OpenAI API key vereist voor OpenAI mode")
            openai.api_key = openai_api_key
        
        # Commando handlers
        self.command_handlers: Dict[str, Callable] = {}
        self.setup_default_handlers()
        
        # State
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.listen_thread: Optional[threading.Thread] = None
        
    def setup_default_handlers(self):
        """Setup standaard commando handlers"""
        self.register_command("stop", self.handle_stop)
        self.register_command("sta op", self.handle_stand)
        self.register_command("ga zitten", self.handle_sit)
        self.register_command("stop", self.handle_stop)
        self.register_command("model", self.handle_model_select)
        self.register_command("start", self.handle_start)
        self.register_command("help", self.handle_help)
    
    def register_command(self, pattern: str, handler: Callable):
        """
        Registreer commando handler
        
        Args:
            pattern: Commando patroon (regex of tekst)
            handler: Functie die wordt aangeroepen
        """
        self.command_handlers[pattern] = handler
    
    def speak(self, text: str):
        """Spreek tekst uit"""
        print(f"🤖 Robot zegt: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_once(self, timeout: float = 5.0) -> Optional[str]:
        """
        Luister één keer naar spraak
        
        Args:
            timeout: Timeout in seconden
            
        Returns:
            Herkende tekst of None
        """
        try:
            with self.microphone as source:
                # Aanpassen aan omgevingsgeluid
                print("🔊 Aanpassen aan omgevingsgeluid...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                print("🎤 Luisteren...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Herken spraak
            print("🧠 Spraak herkennen...")
            
            if self.use_openai:
                # Gebruik OpenAI Whisper (betere kwaliteit)
                return self._recognize_with_openai(audio)
            else:
                # Gebruik Google Speech Recognition
                try:
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    return text
                except sr.UnknownValueError:
                    print("⚠️  Spraak niet herkend")
                    return None
                except sr.RequestError as e:
                    print(f"❌ Fout bij spraakherkenning: {e}")
                    return None
                    
        except sr.WaitTimeoutError:
            print("⏱️  Timeout - geen spraak gedetecteerd")
            return None
        except Exception as e:
            print(f"❌ Fout: {e}")
            return None
    
    def _recognize_with_openai(self, audio) -> Optional[str]:
        """Gebruik OpenAI Whisper voor spraakherkenning"""
        try:
            # Converteer audio naar WAV
            import io
            import wave
            
            wav_data = io.BytesIO()
            with wave.open(wav_data, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(audio.sample_width)
                wav_file.setframerate(audio.sample_rate)
                wav_file.writeframes(audio.get_raw_data())
            
            wav_data.seek(0)
            
            # OpenAI Whisper API
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=wav_data,
                language="nl" if "nl" in self.language else "en"
            )
            
            return response["text"]
        except Exception as e:
            print(f"❌ OpenAI fout: {e}")
            return None
    
    def process_command(self, text: str) -> bool:
        """
        Verwerk commando tekst
        
        Args:
            text: Herkende tekst
            
        Returns:
            True als commando werd herkend en uitgevoerd
        """
        if not text:
            return False
        
        text_lower = text.lower().strip()
        print(f"📝 Herkend: {text}")
        
        # Check alle commando patterns
        for pattern, handler in self.command_handlers.items():
            if re.search(pattern.lower(), text_lower):
                try:
                    handler(text)
                    return True
                except Exception as e:
                    print(f"❌ Fout bij uitvoeren commando: {e}")
                    return False
        
        # Geen match gevonden
        print(f"⚠️  Commando niet herkend: {text}")
        return False
    
    def start_listening(self, callback: Optional[Callable] = None):
        """
        Start continue luisteren
        
        Args:
            callback: Functie die wordt aangeroepen bij commando (optioneel)
        """
        if self.is_listening:
            print("⚠️  Luisteren al actief")
            return
        
        self.is_listening = True
        
        def listen_loop():
            while self.is_listening:
                text = self.listen_once(timeout=3.0)
                if text:
                    if callback:
                        callback(text)
                    else:
                        self.process_command(text)
        
        self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listen_thread.start()
        print("✓ Luisteren gestart")
    
    def stop_listening(self):
        """Stop met luisteren"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1.0)
        print("✓ Luisteren gestopt")
    
    # Commando handlers (moeten worden geïmplementeerd door subclasses)
    def handle_stop(self, text: str):
        """Handle stop commando"""
        raise NotImplementedError("Implementeer in subclass")
    
    def handle_stand(self, text: str):
        """Handle stand commando"""
        raise NotImplementedError("Implementeer in subclass")
    
    def handle_sit(self, text: str):
        """Handle sit commando"""
        raise NotImplementedError("Implementeer in subclass")
    
    def handle_model_select(self, text: str):
        """Handle model selectie commando"""
        raise NotImplementedError("Implementeer in subclass")
    
    def handle_start(self, text: str):
        """Handle start commando"""
        raise NotImplementedError("Implementeer in subclass")
    
    def handle_help(self, text: str):
        """Handle help commando"""
        help_text = """
Beschikbare commando's:
- "sta op" - Laat robot rechtop staan
- "ga zitten" - Laat robot zitten
- "stop" - Stop alle beweging
- "model [naam]" - Selecteer RL model
- "start" - Start RL control
- "help" - Toon deze help
        """
        print(help_text)
        self.speak("Beschikbare commando's: sta op, ga zitten, stop, model selecteren, start, help")


class Go2VoiceController(VoiceController):
    """
    Voice controller specifiek voor Go2 robot met RL model integratie
    """
    
    def __init__(
        self,
        robot=None,
        api_base: Optional[str] = None,
        **kwargs
    ):
        """
        Initialiseer Go2 voice controller
        
        Args:
            robot: Go2Robot instantie (optioneel)
            api_base: API server URL (bijv. "http://localhost:5000/api")
            **kwargs: Extra argumenten voor VoiceController
        """
        super().__init__(**kwargs)
        
        self.robot = robot
        self.api_base = api_base
        
        # State
        self.current_model: Optional[str] = None
        self.is_controlling = False
        
        # Setup specifieke handlers
        self.setup_go2_handlers()
    
    def setup_go2_handlers(self):
        """Setup Go2 specifieke commando handlers"""
        # Model selectie patterns
        self.register_command(r"model\s+(\w+)", self.handle_model_select)
        self.register_command(r"gebruik\s+model\s+(\w+)", self.handle_model_select)
        self.register_command(r"selecteer\s+model\s+(\w+)", self.handle_model_select)
        
        # Control patterns
        self.register_command(r"start\s+rl", self.handle_start)
        self.register_command(r"start\s+control", self.handle_start)
        self.register_command(r"stop\s+rl", self.handle_stop)
        self.register_command(r"stop\s+control", self.handle_stop)
    
    def handle_stop(self, text: str):
        """Stop robot beweging"""
        if self.robot:
            try:
                self.robot.stop()
                self.speak("Robot gestopt")
            except Exception as e:
                self.speak(f"Fout bij stoppen: {e}")
        elif self.api_base:
            import requests
            try:
                requests.post(f"{self.api_base}/control/stop")
                requests.post(f"{self.api_base}/robot/command", json={"command": "stop"})
                self.speak("Robot gestopt")
            except Exception as e:
                self.speak(f"Fout bij stoppen: {e}")
        else:
            self.speak("Geen robot verbinding")
    
    def handle_stand(self, text: str):
        """Laat robot rechtop staan"""
        if self.robot:
            try:
                self.robot.stand()
                self.speak("Robot staat rechtop")
            except Exception as e:
                self.speak(f"Fout: {e}")
        elif self.api_base:
            import requests
            try:
                requests.post(f"{self.api_base}/robot/command", json={"command": "stand"})
                self.speak("Robot staat rechtop")
            except Exception as e:
                self.speak(f"Fout: {e}")
        else:
            self.speak("Geen robot verbinding")
    
    def handle_sit(self, text: str):
        """Laat robot zitten"""
        if self.robot:
            try:
                self.robot.sit()
                self.speak("Robot gaat zitten")
            except Exception as e:
                self.speak(f"Fout: {e}")
        elif self.api_base:
            import requests
            try:
                requests.post(f"{self.api_base}/robot/command", json={"command": "sit"})
                self.speak("Robot gaat zitten")
            except Exception as e:
                self.speak(f"Fout: {e}")
        else:
            self.speak("Geen robot verbinding")
    
    def handle_model_select(self, text: str):
        """Selecteer RL model"""
        # Extract model naam uit tekst
        match = re.search(r"model\s+(\w+)|gebruik\s+model\s+(\w+)|selecteer\s+model\s+(\w+)", text.lower())
        if match:
            model_name = match.group(1) or match.group(2) or match.group(3)
        else:
            # Probeer laatste woord als model naam
            words = text.lower().split()
            if "model" in words:
                idx = words.index("model")
                if idx + 1 < len(words):
                    model_name = words[idx + 1]
                else:
                    self.speak("Welk model wil je gebruiken?")
                    return
            else:
                self.speak("Welk model wil je gebruiken?")
                return
        
        if self.api_base:
            import requests
            try:
                # Laad model
                response = requests.post(f"{self.api_base}/models/{model_name}/load")
                if response.status_code != 200:
                    self.speak(f"Model {model_name} niet gevonden")
                    return
                
                # Activeer model
                requests.post(f"{self.api_base}/models/{model_name}/activate")
                self.current_model = model_name
                self.speak(f"Model {model_name} geactiveerd")
            except Exception as e:
                self.speak(f"Fout bij laden model: {e}")
        else:
            self.speak("API server niet beschikbaar")
    
    def handle_start(self, text: str):
        """Start RL control"""
        if not self.current_model:
            self.speak("Selecteer eerst een model")
            return
        
        if self.api_base:
            import requests
            try:
                requests.post(f"{self.api_base}/control/start")
                self.is_controlling = True
                self.speak(f"RL control gestart met model {self.current_model}")
            except Exception as e:
                self.speak(f"Fout bij starten: {e}")
        else:
            self.speak("API server niet beschikbaar")

