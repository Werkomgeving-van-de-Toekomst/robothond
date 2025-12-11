# Voice Processing op Jetson AGX Orin

Complete guide voor het gebruik van de Jetson AGX Orin als voice processing server voor de Go2 robot.

## Overzicht

De Jetson AGX Orin biedt extra rekenkracht voor:
- **Real-time spraakherkenning** met grote Whisper modellen
- **Lage latency** door lokale processing
- **Betere accuratesse** met medium/large Whisper modellen
- **Onboard audio processing** zonder externe services
- **Volledige Nederlandse ondersteuning** voor spraakcommando's

## Architectuur Opties

Er zijn twee manieren om audio naar de Jetson te krijgen:

### Optie 1: Microfoon Direct op Jetson

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Microfoon     │         │  Jetson AGX Orin  │         │  Go2 Robot  │
│   (Jetson)      │────────▶│  Voice Server     │────────▶│             │
│                 │  Audio  │  - Whisper        │  UDP    │             │
└─────────────────┘         │  - Commando's     │         └─────────────┘
                            │  - Robot Control  │
                            └──────────────────┘
```

**Voordelen**:
- Eenvoudigste setup
- Directe audio input
- Geen netwerk latency voor audio

**Nadelen**:
- Microfoon moet dichtbij Jetson zijn
- Mogelijk niet optimaal gepositioneerd voor robot interactie

### Optie 2: Microfoon op Go2 Robot (Audio Streaming)

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Go2 Robot     │         │  Jetson AGX Orin  │         │  Go2 Robot  │
│   Microfoon     │────────▶│  Voice Server     │────────▶│  (Control)  │
│                 │  Audio  │  - Whisper        │  UDP    │             │
│                 │  Stream │  - Commando's     │         └─────────────┘
└─────────────────┘         │  - Robot Control  │
                            └──────────────────┘
```

**Voordelen**:
- Microfoon op robot (beter gepositioneerd)
- Robot kan zelfstandig luisteren
- Natuurlijkere interactie

**Nadelen**:
- Vereist audio streaming setup
- Netwerk latency voor audio (meestal < 50ms)
- Go2 moet audio streaming ondersteunen

### Optie 3: Externe Microfoon via Netwerk

```
┌─────────────────┐
│   Externe       │
│   Microfoon     │────────┐
│   (USB/Bluetooth)│       │
└─────────────────┘       │
                           │ Audio Stream
                           ▼
                  ┌──────────────────┐         ┌─────────────┐
                  │  Jetson AGX Orin  │         │  Go2 Robot  │
                  │  Voice Server     │────────▶│             │
                  │  - Whisper        │  UDP    │             │
                  │  - Commando's     │         └─────────────┘
                  └──────────────────┘
```

## Installatie op Jetson

### Stap 1: Installeer Dependencies

```bash
# Activeer Python environment
source ~/go2_venv/bin/activate  # Of jouw venv

# Installeer voice dependencies
pip install SpeechRecognition pyttsx3 pyaudio openai-whisper scipy flask flask-cors requests

# Voor audio input (als microfoon op Jetson)
sudo apt install -y portaudio19-dev python3-pyaudio
```

### Stap 2: Test Microfoon (Als microfoon op Jetson)

```bash
# Check beschikbare audio devices
python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"

# Test audio opname
python3 -c "
import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 3

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
print('Opnemen...')
frames = [stream.read(CHUNK) for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS))]
print('Klaar!')
stream.stop_stream()
stream.close()
p.terminate()
"
```

### Stap 3: Download Whisper Model

De eerste keer dat je Whisper gebruikt wordt het model automatisch gedownload:

```bash
python3 -c "import whisper; whisper.load_model('base')"
```

**Model opties** (van klein naar groot):
- `tiny` - ~39 MB, snelste, minste accuratesse
- `base` - ~74 MB, goede balans (aanbevolen voor start)
- `small` - ~244 MB, betere kwaliteit
- `medium` - ~769 MB, zeer goede kwaliteit (aanbevolen voor Jetson)
- `large` - ~1550 MB, beste kwaliteit, langzaamste

**Voor Jetson AGX Orin**: Gebruik `medium` of `large` voor beste resultaten.

**Nederlandse ondersteuning**: Alle Whisper modellen ondersteunen Nederlands uitstekend. De Jetson kan grote modellen draaien voor optimale Nederlandse spraakherkenning.

## Configuratie

### Netwerk Setup

Zorg dat Jetson verbonden is met Go2 robot:

```bash
# Test verbinding
ping 192.168.123.161

# Check interface naam
ip link show  # Meestal eth0
```

### Start Voice Server

#### Basis Configuratie (Nederlands)

```bash
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --port 8888 \
    --whisper-model base \
    --language nl-NL  # Nederlands
```

#### Met Groot Model (Beste Nederlandse Kwaliteit)

```bash
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --port 8888 \
    --whisper-model medium \
    --language nl-NL  # Nederlands (aanbevolen voor beste kwaliteit)
```

#### Met Large Model (Beste Kwaliteit)

```bash
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --port 8888 \
    --whisper-model large \
    --language nl-NL  # Nederlands
```

#### Zonder Robot Verbinding (Alleen Voice Processing)

```bash
python3 src/voice/jetson_voice_server.py \
    --no-robot \
    --port 8888 \
    --whisper-model medium \
    --language nl-NL  # Nederlands
```

## API Endpoints

### Health Check

```bash
curl http://192.168.1.100:8888/health
```

Response:
```json
{
  "status": "ok",
  "robot_connected": true,
  "whisper_model": "medium",
  "language": "nl-NL"
}
```

### Stuur Tekst Commando (Nederlands)

```bash
# Nederlandse commando's worden volledig ondersteund
curl -X POST http://192.168.1.100:8888/api/voice/listen \
  -H "Content-Type: application/json" \
  -d '{"text": "sta op"}'
```

Response:
```json
{
  "status": "ok",
  "recognized": "sta op",
  "processed": true,
  "response": "Robot staat rechtop"
}
```

**Nederlandse commando voorbeelden**:
- `"sta op"` of `"sta rechtop"` - Robot staat rechtop
- `"ga zitten"` of `"zit"` - Robot gaat zitten
- `"stop"` of `"stoppen"` - Stop beweging
- `"zoek [term]"` of `"vind [term]"` - Zoek op internet
- `"help"` of `"hulp"` - Toon commando's

### Start Continue Luisteren

```bash
curl -X POST http://192.168.1.100:8888/api/voice/start
```

### Stop Luisteren

```bash
curl -X POST http://192.168.1.100:8888/api/voice/stop
```

### Get Status

```bash
curl http://192.168.1.100:8888/api/voice/status
```

### Stuur Direct Robot Commando

```bash
curl -X POST http://192.168.1.100:8888/api/robot/command \
  -H "Content-Type: application/json" \
  -d '{"command": "stand"}'
```

## Gebruik Client Script

### Vanaf Jetson (Lokaal)

```bash
# Stuur Nederlands commando
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://localhost:8888 \
    --command "sta op"

# Check status
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://localhost:8888 \
    --status

# Start luisteren
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://localhost:8888 \
    --start
```

### Vanaf Andere Computer

```bash
# Vervang localhost met Jetson IP
# Nederlandse commando's worden volledig ondersteund
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.1.100:8888 \
    --command "ga zitten"

# Andere Nederlandse commando's
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.1.100:8888 \
    --command "zoek unitree go2"

python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.1.100:8888 \
    --command "stop"
```

## Beschikbare Commando's

- **"sta op"** / **"sta rechtop"** - Laat robot rechtop staan
- **"ga zitten"** / **"zit"** - Laat robot zitten
- **"stop"** - Stop alle beweging
- **"model [naam]"** - Selecteer RL model
- **"start"** - Start RL control
- **"zoek [term]"** / **"vind [term]"** - Zoek op internet
- **"help"** - Toon beschikbare commando's

## Performance Optimalisatie

### Jetson Power Mode

Voor beste performance bij voice processing:

```bash
# Set naar max performance
sudo nvpmodel -m 0
sudo jetson_clocks

# Check status
sudo tegrastats
```

### Whisper Model Keuze

| Model | Grootte | Snelheid | Accuratesse | Aanbevolen voor |
|-------|---------|----------|-------------|-----------------|
| tiny  | 39 MB   | Zeer snel | Laag        | Testen          |
| base  | 74 MB   | Snel      | Goed        | Standaard       |
| small | 244 MB  | Medium    | Zeer goed   | Productie       |
| medium| 769 MB  | Langzaam  | Excellent   | **Jetson (aanbevolen)** |
| large | 1550 MB | Zeer langzaam | Beste    | Beste kwaliteit |

### Audio Optimalisatie

```bash
# Check audio latency
# Gebruik ALSA voor lage latency
sudo nano /etc/asound.conf

# Voeg toe:
pcm.!default {
    type hw
    card 0
    device 0
}

ctl.!default {
    type hw
    card 0
}
```

## Troubleshooting

### Probleem: Microfoon niet gedetecteerd

```bash
# Check audio devices
arecord -l

# Test opname
arecord -d 3 test.wav
aplay test.wav
```

### Probleem: Whisper model te langzaam

1. **Gebruik kleiner model**:
   ```bash
   python3 src/voice/jetson_voice_server.py --whisper-model base
   ```

2. **Check Jetson performance**:
   ```bash
   sudo tegrastats
   # Check of GPU/CPU niet overbelast zijn
   ```

3. **Set max performance**:
   ```bash
   sudo nvpmodel -m 0
   sudo jetson_clocks
   ```

### Probleem: Robot niet verbonden

```bash
# Test robot verbinding
ping 192.168.123.161

# Check interface
ip addr show eth0

# Test SDK verbinding
python3 -c "
from src.unitree_go2 import Go2RobotOfficial
robot = Go2RobotOfficial(ip_address='192.168.123.161', network_interface='eth0')
robot.connect()
print('OK')
robot.disconnect()
"
```

### Probleem: Hoge latency

1. **Gebruik directe Ethernet verbinding** (niet via router)
2. **Disable power management**:
   ```bash
   echo "on" | sudo tee /sys/class/net/eth0/power/control
   ```
3. **Check netwerk buffers**:
   ```bash
   sudo sysctl -w net.core.rmem_max=134217728
   sudo sysctl -w net.core.wmem_max=134217728
   ```

## Use Cases

### 1. Onboard Voice Control

Microfoon direct op Jetson, alles lokaal:

```bash
# Start server met microfoon op Jetson
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --whisper-model medium
```

### 2. Remote Voice Control

Client stuurt commando's naar Jetson:

```bash
# Op Jetson: Start server
python3 src/voice/jetson_voice_server.py --port 8888

# Op client: Stuur commando's
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.1.100:8888 \
    --command "sta op"
```

### 3. Multi-Client Setup

Meerdere clients kunnen commando's sturen:

```bash
# Client 1
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.1.100:8888 \
    --command "sta op"

# Client 2 (tegelijkertijd)
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.1.100:8888 \
    --command "ga zitten"
```

## Integratie met Bestaande Systemen

### Met API Server

```python
# Jetson voice server kan commando's naar API server sturen
import requests

# Stuur commando naar API server
response = requests.post(
    "http://api-server:5000/api/voice/command",
    json={"command": "sta op"}
)
```

### Met ROS2

```python
# Jetson voice server kan ROS2 topics publiceren
import rclpy
from std_msgs.msg import String

# In voice server code:
node = rclpy.create_node('voice_server')
publisher = node.create_publisher(String, 'voice_commands', 10)

# Bij commando:
msg = String()
msg.data = recognized_text
publisher.publish(msg)
```

## Samenvatting

### Quick Start

```bash
# 1. Installeer dependencies
pip install SpeechRecognition pyttsx3 pyaudio openai-whisper scipy flask flask-cors

# 2. Start voice server
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --whisper-model medium

# 3. Test met client
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://localhost:8888 \
    --command "sta op"
```

### Belangrijke Bestanden

- `src/voice/jetson_voice_server.py` - Voice server voor Jetson
- `src/voice/jetson_voice_client.py` - Client voor commando's
- `src/voice/voice_controller.py` - Basis voice controller

## Multi-Jetson Setup

Voor betere performance en fault tolerance kun je meerdere Jetsons parallel gebruiken:

- **Load Balancing**: Verdeel workload over meerdere Jetsons
- **Redundancy**: Als één Jetson faalt, blijft systeem werken
- **Schaalbaarheid**: Ondersteun meerdere robots of complexere processing
- **Specialisatie**: Verschillende Jetsons voor verschillende taken

Zie [Multi-Jetson Setup](./MULTI_JETSON_SETUP.md) voor complete documentatie.

## Referenties

- [Multi-Jetson Setup](./MULTI_JETSON_SETUP.md) - Meerdere Jetsons parallel gebruiken
- [Jetson AGX Orin Verbinding](./JETSON_AGX_ORIN_VERBINDING.md)
- [Voice Control Guide](./VOICE_CONTROL.md) - Complete voice guide inclusief Nederlandse commando's
- [Voice op Robot](./VOICE_OP_ROBOT.md)
- [OpenAI Whisper GitHub](https://github.com/openai/whisper)
- [NVIDIA Jetson Developer Guide](https://developer.nvidia.com/embedded/jetson-agx-orin)

