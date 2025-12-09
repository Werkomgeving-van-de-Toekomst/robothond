# Voice Processing Direct op Go2 Robot

Complete guide voor het draaien van voice processing direct op de Go2 robot zelf, zonder externe Jetson.

## Overzicht

De Go2 robot heeft een **onboard computer** die voice processing kan uitvoeren. Dit heeft voordelen:
- **Geen externe hardware nodig**
- **Lagere latency** (alles lokaal)
- **Autonome operatie** (robot werkt zelfstandig)
- **Eenvoudigere setup** (geen extra apparaten)

## Beperkingen en Overwegingen

### Hardware Beperkingen

De Go2 robot heeft **beperkte rekenkracht** vergeleken met Jetson AGX Orin:

| Feature | Go2 Robot | Jetson AGX Orin |
|---------|-----------|-----------------|
| Processor | ARM (onboard) | NVIDIA ARM + GPU |
| RAM | Beperkt | 32GB+ |
| Whisper Model | tiny/base (aanbevolen) | medium/large mogelijk |
| Real-time | Ja (kleinere modellen) | Ja (grote modellen) |

### Aanbevolen Configuratie

Voor voice processing op de robot zelf:
- **Whisper Model**: `tiny` of `base` (niet groter)
- **Gebruik**: Eenvoudige commando's, niet complexe spraak
- **Alternatief**: Google Speech Recognition API (cloud-based)

## Installatie op Robot

### Stap 1: Check Robot Toegang

De Go2 robot heeft SSH toegang mogelijk (afhankelijk van model en configuratie):

```bash
# Probeer SSH verbinding
ssh unitree@192.168.123.161
# Of:
ssh root@192.168.123.161
```

**Let op**: Niet alle Go2 modellen hebben SSH toegang. Check je model specificaties.

### Stap 2: Check Python op Robot

```bash
# Check Python versie
python3 --version

# Check beschikbare packages
pip3 list
```

### Stap 3: Installeer Dependencies

```bash
# Op robot (via SSH of via SDK deployment)
pip3 install SpeechRecognition pyttsx3 pyaudio

# Voor Whisper (klein model!)
pip3 install openai-whisper scipy

# Optioneel: voor audio
sudo apt install -y portaudio19-dev python3-pyaudio
```

### Stap 4: Deploy Voice Code naar Robot

#### Methode 1: Via SSH (Als beschikbaar)

```bash
# Kopieer code naar robot
scp -r src/voice unitree@192.168.123.161:/home/unitree/
scp -r src/unitree_go2 unitree@192.168.123.161:/home/unitree/
```

#### Methode 2: Via SDK Deployment Script

Maak een deployment script:

```python
#!/usr/bin/env python3
"""Deploy voice code naar Go2 robot"""

import paramiko
import os

def deploy_to_robot(robot_ip="192.168.123.161", username="unitree"):
    """Deploy voice code naar robot"""
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(robot_ip, username=username)
        sftp = ssh.open_sftp()
        
        # Upload voice controller
        sftp.put("src/voice/voice_controller.py", "/home/unitree/voice_controller.py")
        
        # Upload robot SDK
        # ... upload robot code ...
        
        sftp.close()
        ssh.close()
        print("✓ Code geüpload naar robot")
        
    except Exception as e:
        print(f"❌ Fout: {e}")
```

## Gebruik op Robot

### Basis Voice Control Script voor Robot

Maak een aangepaste versie die op de robot draait:

```python
#!/usr/bin/env python3
"""
Voice Control Direct op Go2 Robot

Dit script draait op de robot zelf en gebruikt lokale resources.
"""

import sys
import os
from pathlib import Path

# Voeg robot SDK toe
sys.path.insert(0, '/home/unitree/unitree_sdk2_python')

from voice_controller import Go2VoiceController
from unitree_sdk2_python.go2.sport import SportClient
from unitree_sdk2_python.go2.robot_state import RobotStateClient

class RobotVoiceController:
    """Voice controller die direct op robot draait"""
    
    def __init__(self):
        # Gebruik kleine Whisper model (tiny of base)
        self.voice_controller = Go2VoiceController(
            robot=None,  # We gebruiken direct SDK
            language="nl-NL",
            use_whisper=True,
            whisper_model="tiny",  # Klein model voor robot!
            use_openai_api=False
        )
        
        # Robot SDK clients
        self.sport_client = SportClient()
        self.state_client = RobotStateClient()
        
    def handle_stand(self, text: str):
        """Laat robot rechtop staan"""
        self.sport_client.stand_up()
        self.voice_controller.speak("Ik sta rechtop")
    
    def handle_sit(self, text: str):
        """Laat robot zitten"""
        self.sport_client.sit_down()
        self.voice_controller.speak("Ik ga zitten")
    
    def handle_stop(self, text: str):
        """Stop beweging"""
        self.sport_client.stop()
        self.voice_controller.speak("Ik stop")
    
    def run(self):
        """Start voice control loop"""
        print("🎤 Voice control gestart op robot")
        self.voice_controller.speak("Ik luister. Zeg een commando.")
        
        self.voice_controller.start_listening()
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stoppen...")
            self.voice_controller.stop_listening()

if __name__ == "__main__":
    controller = RobotVoiceController()
    controller.run()
```

### Start Voice Control op Robot

```bash
# Via SSH
ssh unitree@192.168.123.161
cd /home/unitree
python3 robot_voice_control.py
```

## Alternatieve Aanpak: Cloud Speech Recognition

Als de robot te weinig rekenkracht heeft, gebruik cloud-based speech recognition:

### Google Speech Recognition (Gratis, Beperkt)

```python
# In voice_controller.py
# Gebruik Google Speech Recognition (geen Whisper nodig)
controller = Go2VoiceController(
    robot=robot,
    use_whisper=False,  # Geen lokale Whisper
    use_openai_api=False  # Geen OpenAI API
)
# Gebruikt standaard Google Speech Recognition
```

**Voordelen**:
- Geen lokale rekenkracht nodig
- Werkt op robot zelf
- Gratis (beperkt aantal requests)

**Nadelen**:
- Vereist internet verbinding
- Latency door cloud
- Beperkte gratis quota

### OpenAI Whisper API (Cloud)

```python
controller = Go2VoiceController(
    robot=robot,
    use_whisper=False,
    use_openai_api=True,  # Gebruik cloud API
    openai_api_key="jouw-key"
)
```

**Voordelen**:
- Zeer goede kwaliteit
- Geen lokale rekenkracht nodig
- Werkt op robot zelf

**Nadelen**:
- Vereist internet
- Kosten per gebruik
- Latency door cloud

## Vergelijking: Robot vs Jetson

### Wanneer Robot Zelf Gebruiken?

✅ **Gebruik robot zelf als**:
- Je eenvoudige commando's nodig hebt
- Je geen externe hardware wilt
- Latency kritiek is (alles lokaal)
- Robot autonoom moet werken
- Budget beperkt is

### Wanneer Jetson Gebruiken?

✅ **Gebruik Jetson als**:
- Je complexe spraak nodig hebt
- Je grote Whisper modellen wilt (medium/large)
- Je meerdere taken tegelijk doet
- Je beste kwaliteit wilt
- Je extra AI processing nodig hebt

## Optimalisatie voor Robot

### 1. Gebruik Klein Whisper Model

```python
# Gebruik tiny model (snelste, minste geheugen)
whisper_model="tiny"

# Of base (betere kwaliteit, nog steeds snel)
whisper_model="base"
```

### 2. Beperk Audio Buffer

```python
# In voice_controller.py
# Gebruik kortere audio buffers
audio = self.recognizer.listen(source, timeout=2.0, phrase_time_limit=3.0)
```

### 3. Disable Onnodige Features

```python
# Geen web search op robot (teveel resources)
web_searcher=None

# Geen display server
display_api_url=None
```

### 4. Gebruik Threading Efficiënt

```python
# Process commando's in background thread
# Maar beperk aantal threads
```

## Troubleshooting

### Probleem: Robot heeft geen SSH toegang

**Oplossing**: Gebruik SDK deployment of werk via netwerk API.

### Probleem: Whisper model te groot

**Oplossing**: Gebruik `tiny` model of Google Speech Recognition.

### Probleem: Robot heeft geen microfoon

**Oplossing**: 
- Gebruik externe USB microfoon
- Of gebruik remote voice control (commando's vanaf andere computer)

### Probleem: Te weinig geheugen

**Oplossing**:
- Gebruik kleinere Whisper model
- Of gebruik cloud-based speech recognition
- Sluit andere applicaties

### Probleem: Hoge CPU gebruik

**Oplossing**:
- Gebruik `tiny` Whisper model
- Verhoog timeout tussen commando's
- Gebruik cloud API in plaats van lokale Whisper

## Best Practices

### 1. Start Simpel

Begin met `tiny` Whisper model en Google Speech Recognition:

```python
controller = Go2VoiceController(
    robot=robot,
    use_whisper=True,
    whisper_model="tiny",  # Kleinste model
    use_openai_api=False
)
```

### 2. Test Performance

Monitor CPU en geheugen gebruik:

```bash
# Op robot (via SSH)
top
# Of:
htop
```

### 3. Gebruik Cloud als Backup

Als lokale processing te traag is, fallback naar cloud:

```python
try:
    # Probeer lokale Whisper
    text = self._recognize_with_whisper(audio)
except:
    # Fallback naar Google Speech Recognition
    text = self.recognizer.recognize_google(audio, language=self.language)
```

## Voorbeeld: Complete Setup op Robot

```python
#!/usr/bin/env python3
"""Complete voice control setup voor Go2 robot"""

import sys
sys.path.insert(0, '/home/unitree/unitree_sdk2_python')

from voice_controller import Go2VoiceController
from unitree_sdk2_python.go2.sport import SportClient

# Initialiseer robot SDK
sport_client = SportClient()

# Maak voice controller (klein model!)
controller = Go2VoiceController(
    robot=None,  # We gebruiken direct SDK
    language="nl-NL",
    use_whisper=True,
    whisper_model="tiny",  # Klein model!
    use_openai_api=False
)

# Setup handlers
def handle_stand(text):
    sport_client.stand_up()
    controller.speak("Ik sta rechtop")

def handle_sit(text):
    sport_client.sit_down()
    controller.speak("Ik ga zitten")

controller.register_command("sta op", handle_stand)
controller.register_command("ga zitten", handle_sit)

# Start
print("🎤 Voice control op robot gestart")
controller.speak("Ik luister. Zeg een commando.")
controller.start_listening()

# Keep running
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    controller.stop_listening()
    print("Gestopt")
```

## Samenvatting

### Quick Start op Robot

```bash
# 1. Installeer dependencies (via SSH of deployment)
pip3 install SpeechRecognition pyttsx3 openai-whisper scipy

# 2. Gebruik klein Whisper model
python3 robot_voice_control.py --whisper-model tiny

# 3. Of gebruik Google Speech Recognition (geen Whisper)
python3 robot_voice_control.py  # Standaard gebruikt Google
```

### Aanbevelingen

| Scenario | Aanbeveling |
|----------|-------------|
| Eenvoudige commando's | Robot zelf met `tiny` Whisper |
| Betere kwaliteit | Robot met Google Speech Recognition |
| Beste kwaliteit | Jetson met `medium/large` Whisper |
| Geen internet | Robot zelf met `tiny/base` Whisper |
| Autonome operatie | Robot zelf |

## Referenties

- [Voice Control Guide](./VOICE_CONTROL.md)
- [Jetson Voice Processing](./JETSON_VOICE_PROCESSING.md)
- [Go2 SDK Referentie](./GO2_SDK_REFERENTIE.md)

