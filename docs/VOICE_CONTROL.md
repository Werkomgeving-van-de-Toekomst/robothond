# Voice Control voor Go2 Robot

Deze guide beschrijft hoe je tegen de Go2 robot kunt praten en commando's kunt geven via spraak.

## Overzicht

Het voice control systeem ondersteunt:
- **Spraakherkenning**: Nederlands en Engels
- **Commando interpretatie**: Herkent commando's en voert acties uit
- **Text-to-Speech**: Robot spreekt terug
- **RL Model selectie**: Selecteer modellen via spraak
- **Robot besturing**: Basis commando's (stand, sit, stop)

## Installatie

### Stap 1: Installeer Dependencies

```bash
conda activate pybullet  # Of je normale venv
pip install SpeechRecognition pyttsx3 pyaudio
```

**Op macOS** kan je ook PortAudio nodig hebben:
```bash
brew install portaudio
pip install pyaudio
```

### Stap 2: Optioneel - OpenAI Whisper (Betere kwaliteit)

Voor betere spraakherkenning kun je OpenAI Whisper gebruiken:

```bash
pip install openai
export OPENAI_API_KEY="jouw-api-key"
```

## Basis Gebruik

### Directe Robot Verbinding

```bash
python src/examples/voice_control.py --robot-ip 192.168.123.161
```

### Via API Server

```bash
# Terminal 1: Start API server
python src/controller_app/model_api_server.py --host 0.0.0.0 --port 5000

# Terminal 2: Start voice control
python src/examples/voice_control.py --api http://localhost:5000/api
```

### Met OpenAI Whisper

```bash
python src/examples/voice_control.py \
    --api http://localhost:5000/api \
    --openai \
    --openai-key jouw-api-key
```

## Beschikbare Commando's

### Basis Commando's

- **"sta op"** - Laat robot rechtop staan
- **"ga zitten"** - Laat robot zitten  
- **"stop"** - Stop alle beweging
- **"help"** - Toon beschikbare commando's

### RL Model Commando's

- **"model [naam]"** - Selecteer RL model (bijv. "model go2_rl")
- **"gebruik model [naam]"** - Selecteer model
- **"selecteer model [naam]"** - Selecteer model
- **"start"** of **"start rl"** - Start RL control
- **"stop rl"** - Stop RL control

### Voorbeelden

```
Jij: "model go2_rl"
Robot: "Model go2_rl geactiveerd"

Jij: "start"
Robot: "RL control gestart met model go2_rl"

Jij: "sta op"
Robot: "Robot staat rechtop"

Jij: "stop"
Robot: "Robot gestopt"
```

## Python API

### Basis Gebruik

```python
from src.voice.voice_controller import Go2VoiceController
from src.unitree_go2.robot import Go2Robot

# Connect robot
robot = Go2Robot()
robot.connect()

# Maak voice controller
controller = Go2VoiceController(
    robot=robot,
    language="nl-NL"
)

# Luister één keer
text = controller.listen_once()
if text:
    controller.process_command(text)

# Of start continue luisteren
controller.start_listening()
```

### Met API Server

```python
controller = Go2VoiceController(
    api_base="http://localhost:5000/api",
    language="nl-NL"
)

controller.start_listening()
```

### Custom Commando's

```python
def handle_custom_command(text: str):
    print(f"Custom commando: {text}")

controller = Go2VoiceController(robot=robot)
controller.register_command("mijn commando", handle_custom_command)
controller.start_listening()
```

## Integratie met Unitree Go App

Je kunt voice control ook gebruiken via de API server:

### Via API Endpoint

```bash
# Stuur voice commando via API
curl -X POST http://localhost:5000/api/voice/command \
  -H "Content-Type: application/json" \
  -d '{"command": "model go2_rl"}'
```

### Via Unitree Go App Programming

Maak een programma in de app dat:
1. Gebruikt microfoon input
2. Stuurt tekst naar `/api/voice/command`
3. Toont antwoord

## Troubleshooting

### Microfoon werkt niet

- **macOS**: Check microfoon permissies in System Preferences
- **Linux**: Check of je in `audio` groep zit: `groups`
- **Test microfoon**: Gebruik `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`

### Spraak niet herkend

- **Spreek duidelijk**: Zorg voor rustige omgeving
- **Check taal**: Verifieer `--language` parameter
- **Gebruik OpenAI**: Probeer `--openai` voor betere herkenning
- **Test eerst**: Test met `listen_once()` om te zien of microfoon werkt

### PyAudio installatie problemen

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

**Linux**:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**Windows**:
```bash
pip install pipwin
pipwin install pyaudio
```

### OpenAI API Key

1. Maak account op https://platform.openai.com
2. Genereer API key
3. Export als environment variable:
   ```bash
   export OPENAI_API_KEY="jouw-key"
   ```
4. Of gebruik `--openai-key` parameter

## Geavanceerd Gebruik

### Custom Commando Patterns

```python
import re

def handle_custom(text: str):
    # Extract nummer uit commando
    match = re.search(r"ga\s+(\d+)\s+meter", text.lower())
    if match:
        meters = int(match.group(1))
        # Voer actie uit
        pass

controller.register_command(r"ga\s+\d+\s+meter", handle_custom)
```

### Multi-language Support

```python
# Wissel tussen talen
controller = Go2VoiceController(language="nl-NL")
# Of
controller = Go2VoiceController(language="en-US")
```

### Voice Feedback Aanpassen

```python
# Verander spreeksnelheid
controller.tts_engine.setProperty('rate', 200)  # Sneller

# Verander volume
controller.tts_engine.setProperty('volume', 0.5)  # Zachter

# Verander stem (als beschikbaar)
voices = controller.tts_engine.getProperty('voices')
if voices:
    controller.tts_engine.setProperty('voice', voices[0].id)
```

## Veiligheid

⚠️ **BELANGRIJK**:

1. **Test eerst**: Test commando's eerst zonder robot beweging
2. **Emergency stop**: Zorg dat je snel kunt stoppen
3. **Beperk commando's**: Registreer alleen veilige commando's
4. **Monitor**: Houd robot altijd in de gaten tijdens voice control

## Voorbeelden

### Voorbeeld 1: Basis Voice Control

```bash
python src/examples/voice_control.py --robot-ip 192.168.123.161
```

Zeg dan:
- "sta op"
- "ga zitten"
- "stop"

### Voorbeeld 2: RL Model Selectie

```bash
# Start API server
python src/controller_app/model_api_server.py

# Start voice control
python src/examples/voice_control.py --api http://localhost:5000/api
```

Zeg dan:
- "model go2_rl"
- "start"
- "stop"

### Voorbeeld 3: Custom Script

```python
from src.voice.voice_controller import Go2VoiceController
from src.unitree_go2.robot import Go2Robot

robot = Go2Robot()
robot.connect()

controller = Go2VoiceController(robot=robot)

# Custom handler
def handle_walk(text):
    robot.move(vx=0.3, vy=0.0, vyaw=0.0)
    controller.speak("Robot loopt vooruit")

controller.register_command("loop", handle_walk)
controller.start_listening()

# Wacht op commando's
import time
time.sleep(60)  # Luister 60 seconden

controller.stop_listening()
robot.disconnect()
```

## Volgende Stappen

1. **Test microfoon**: Zorg dat microfoon werkt
2. **Test commando's**: Test alle commando's
3. **Integreer met app**: Gebruik via API server
4. **Voeg custom commando's toe**: Pas aan voor jouw gebruik
5. **Fine-tune**: Pas taal/herkenning aan indien nodig

