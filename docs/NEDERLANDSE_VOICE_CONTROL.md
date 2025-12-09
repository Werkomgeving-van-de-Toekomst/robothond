# Nederlandse Voice Control voor Go2 Robot

Complete guide voor het gebruik van Nederlandse spraakcommando's met de Go2 robot.

## Overzicht

De voice control ondersteunt volledig Nederlands:
- **Spraakherkenning**: Nederlands (nl-NL)
- **Text-to-Speech**: Nederlandse stem (indien beschikbaar)
- **Commando's**: Alle commando's in het Nederlands
- **Whisper**: Ondersteunt Nederlands voor betere accuratesse

## Quick Start

### Basis Gebruik

```bash
# Standaard is al Nederlands ingesteld
python3 src/examples/voice_control.py --robot-ip 192.168.123.161
```

### Met Whisper (Aanbevolen voor Nederlands)

```bash
python3 src/examples/voice_control.py \
    --robot-ip 192.168.123.161 \
    --whisper \
    --whisper-model base \
    --language nl-NL
```

### Op Robot Zelf

```bash
python3 src/examples/voice_control_robot.py \
    --robot-ip 192.168.123.161 \
    --whisper-model tiny \
    --language nl-NL
```

### Met Jetson

```bash
# Op Jetson
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --whisper-model medium \
    --language nl-NL
```

## Nederlandse Commando's

### Basis Bewegingen

| Commando | Alternatieven | Actie |
|----------|---------------|-------|
| **"sta op"** | "sta rechtop", "opstaan", "rechtop staan" | Robot staat rechtop |
| **"ga zitten"** | "zit", "zitten" | Robot gaat zitten |
| **"stop"** | "stoppen", "stop alle" | Stop alle beweging |

### Model Selectie

| Commando | Voorbeeld | Actie |
|----------|-----------|-------|
| **"model [naam]"** | "model basic" | Selecteer RL model |
| **"gebruik model [naam]"** | "gebruik model advanced" | Activeer model |
| **"selecteer model [naam]"** | "selecteer model test" | Selecteer model |
| **"activeer model [naam]"** | "activeer model demo" | Activeer model |

### Control

| Commando | Alternatieven | Actie |
|----------|---------------|-------|
| **"start"** | "begin", "ga" | Start RL control |
| **"start rl"** | "begin rl" | Start RL control |
| **"start besturing"** | "begin besturing" | Start control |

### Internet Zoeken

| Commando | Voorbeeld | Actie |
|----------|-----------|-------|
| **"zoek [term]"** | "zoek unitree go2" | Zoek op internet |
| **"vind [term]"** | "vind robot informatie" | Zoek op internet |
| **"zoek naar [term]"** | "zoek naar nederlandse robots" | Zoek op internet |
| **"zoek op internet [term]"** | "zoek op internet quadrupeds" | Zoek op internet |

### Help

| Commando | Alternatieven | Actie |
|----------|---------------|-------|
| **"help"** | "hulp", "wat kan je", "commando's" | Toon beschikbare commando's |

## Voorbeelden

### Voorbeeld 1: Basis Gebruik

```
Jij: "sta op"
Robot: "Robot staat rechtop" [robot staat op]

Jij: "ga zitten"
Robot: "Robot gaat zitten" [robot gaat zitten]

Jij: "stop"
Robot: "Robot gestopt" [robot stopt]
```

### Voorbeeld 2: Model Selectie

```
Jij: "gebruik model basic"
Robot: "Model basic geactiveerd"

Jij: "start"
Robot: "RL control gestart met model basic"
```

### Voorbeeld 3: Internet Zoeken

```
Jij: "zoek unitree go2"
Robot: "Zoeken naar unitree go2"
Robot: "Ik heb 5 resultaten gevonden en getoond op het scherm"
```

## Configuratie

### Taal Instellen

De standaard taal is al `nl-NL` (Nederlands). Je kunt dit expliciet instellen:

```python
from src.voice.voice_controller import Go2VoiceController

controller = Go2VoiceController(
    robot=robot,
    language="nl-NL",  # Nederlands
    use_whisper=True,
    whisper_model="base"
)
```

### Text-to-Speech (Nederlandse Stem)

De voice controller probeert automatisch een Nederlandse stem te vinden:

```python
# Automatisch ingesteld bij initialisatie
controller = Go2VoiceController(language="nl-NL")
# Probeert Nederlandse stem te vinden
```

**Als geen Nederlandse stem beschikbaar is**:
- Gebruikt beschikbare stem (meestal Engels)
- Spreekt nog steeds Nederlands uit (met accent)
- Werkt nog steeds, maar klinkt mogelijk niet perfect Nederlands

**Voor betere Nederlandse stem**:
- Installeer Nederlandse TTS engine (bijv. espeak-nl)
- Of gebruik cloud-based TTS met Nederlandse stem

## Spraakherkenning Opties

### 1. Google Speech Recognition (Standaard)

```bash
# Geen extra configuratie nodig
python3 src/examples/voice_control.py --robot-ip 192.168.123.161
```

**Voordelen**:
- Werkt direct
- Geen lokale rekenkracht nodig
- Goede Nederlandse ondersteuning

**Nadelen**:
- Vereist internet verbinding
- Beperkte gratis quota

### 2. Lokale Whisper (Aanbevolen)

```bash
python3 src/examples/voice_control.py \
    --robot-ip 192.168.123.161 \
    --whisper \
    --whisper-model base
```

**Voordelen**:
- Werkt offline
- Zeer goede Nederlandse accuratesse
- Geen internet nodig

**Nadelen**:
- Vereist lokale rekenkracht
- Model moet gedownload worden (eerste keer)

### 3. OpenAI Whisper API (Cloud)

```bash
export OPENAI_API_KEY="jouw-key"
python3 src/examples/voice_control.py \
    --robot-ip 192.168.123.161 \
    --openai-api
```

**Voordelen**:
- Beste kwaliteit
- Geen lokale rekenkracht nodig
- Zeer goede Nederlandse ondersteuning

**Nadelen**:
- Vereist internet
- Kosten per gebruik

## Tips voor Betere Herkenning

### 1. Spreek Duidelijk

- Spreek langzaam en duidelijk
- Gebruik korte commando's
- Wacht op bevestiging van robot

### 2. Gebruik Whisper voor Betere Kwaliteit

```bash
# Gebruik base of small model voor beste resultaten
python3 src/examples/voice_control.py \
    --whisper \
    --whisper-model base
```

### 3. Test Microfoon

```bash
# Test microfoon eerst
python3 -c "
from src.voice.voice_controller import VoiceController
vc = VoiceController(language='nl-NL')
print('Zeg iets...')
text = vc.listen_once(timeout=5.0)
print(f'Herkend: {text}')
"
```

### 4. Aanpassen aan Omgeving

De voice controller past automatisch aan omgevingsgeluid aan:

```python
# Automatisch bij eerste luisteren
controller.listen_once()  # Past aan omgevingsgeluid aan
```

## Troubleshooting

### Probleem: Commando's worden niet herkend

**Oplossingen**:
1. **Check taal instelling**:
   ```bash
   # Zorg dat taal op nl-NL staat
   python3 src/examples/voice_control.py --language nl-NL
   ```

2. **Gebruik Whisper**:
   ```bash
   # Whisper heeft betere Nederlandse ondersteuning
   python3 src/examples/voice_control.py --whisper --whisper-model base
   ```

3. **Test microfoon**:
   ```bash
   # Check of microfoon werkt
   python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
   ```

### Probleem: Robot spreekt Engels

**Oplossing**: Check of Nederlandse stem beschikbaar is:

```python
import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(voice.name, voice.id)
    if 'dutch' in voice.name.lower() or 'nl' in voice.id.lower():
        print(f"✓ Nederlandse stem gevonden: {voice.name}")
```

Als geen Nederlandse stem beschikbaar:
- Installeer espeak-nl: `sudo apt install espeak espeak-data espeak-nl`
- Of gebruik cloud-based TTS

### Probleem: Slechte herkenning

**Oplossingen**:
1. **Gebruik groter Whisper model**:
   ```bash
   python3 src/examples/voice_control.py --whisper --whisper-model small
   ```

2. **Verminder achtergrondgeluid**

3. **Spreek langzamer en duidelijker**

4. **Gebruik kortere commando's**

## Aangepaste Nederlandse Commando's Toevoegen

```python
from src.voice.voice_controller import Go2VoiceController

controller = Go2VoiceController(robot=robot, language="nl-NL")

# Voeg custom commando toe
def handle_spring(text):
    controller.robot.move(forward=0.5)
    controller.speak("Ik spring!")

controller.register_command("spring", handle_spring)
controller.register_command("huppel", handle_spring)
controller.register_command("maak een sprong", handle_spring)

# Start luisteren
controller.start_listening()
```

## Samenvatting

### Quick Start Nederlands

```bash
# Eenvoudigste manier (Google Speech Recognition)
python3 src/examples/voice_control.py --robot-ip 192.168.123.161

# Beste kwaliteit (Whisper)
python3 src/examples/voice_control.py \
    --robot-ip 192.168.123.161 \
    --whisper \
    --whisper-model base \
    --language nl-NL
```

### Belangrijkste Commando's

- **"sta op"** - Robot staat rechtop
- **"ga zitten"** - Robot gaat zitten
- **"stop"** - Stop beweging
- **"zoek [term]"** - Zoek op internet
- **"help"** - Toon commando's

## Referenties

- [Voice Control Guide](./VOICE_CONTROL.md)
- [Voice op Robot](./VOICE_OP_ROBOT.md)
- [Jetson Voice Processing](./JETSON_VOICE_PROCESSING.md)

