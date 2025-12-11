# Jetson AGX Orin Project Setup

Complete handleiding voor het opzetten van de projectstructuur op een Jetson AGX Orin voor Go2 robot development.

## Quick Start

### Stap 1: SSH naar Jetson

```bash
# Vanaf je ontwikkel PC
ssh jetson@<jetson-ip-adres>
# Bijvoorbeeld: ssh jetson@192.168.1.100
```

### Stap 2: Download en Run Setup Script

```bash
# Download het setup script
cd ~
wget https://raw.githubusercontent.com/Werkomgeving-van-de-Toekomst/robothond/main/scripts/setup_jetson_project.sh

# Of clone het hele repository eerst
git clone https://github.com/Werkomgeving-van-de-Toekomst/robothond.git
cd robothond
bash scripts/setup_jetson_project.sh
```

### Stap 3: Wacht tot Setup Compleet is

Het script doet automatisch:
- ✅ Projectstructuur aanmaken
- ✅ Git repository clonen
- ✅ Python virtual environment aanmaken
- ✅ Dependencies installeren
- ✅ Netwerk configureren
- ✅ Configuratiebestanden aanmaken

## Projectstructuur

Na setup ziet je project er zo uit:

```
~/go2-ai/
├── src/
│   ├── unitree_go2/      # Go2 SDK wrapper
│   ├── voice/            # Voice processing code
│   ├── examples/         # Voorbeeld scripts
│   └── simulation/       # Simulatie code
├── config/
│   └── robot_config.yaml # Robot configuratie
├── tests/                # Unit tests
├── docs/                 # Documentatie
├── flows/                # Robot flows
├── models/               # AI modellen (Whisper, YOLO)
│   ├── whisper/
│   └── yolo/
├── logs/                 # Log bestanden
├── scripts/              # Utility scripts
├── hardware/             # Hardware designs
├── venv/                 # Python virtual environment
└── .env                  # Environment variabelen
```

## Gebruik

### Virtual Environment Activeren

```bash
# Optie 1: Gebruik alias (toegevoegd aan ~/.bashrc)
go2-activate

# Optie 2: Handmatig
cd ~/go2-ai
source venv/bin/activate
```

### Naar Project Directory

```bash
# Gebruik alias
go2-cd

# Of handmatig
cd ~/go2-ai
```

### Test Verbinding met Robot

```bash
cd ~/go2-ai
./scripts/test_connection.sh
```

### Start Voice Server

```bash
cd ~/go2-ai
./scripts/start_voice_server.sh
```

### Run Voorbeeld Scripts

```bash
cd ~/go2-ai
source venv/bin/activate

# Diagnostics
python src/examples/diagnostics.py

# Basic movement
python src/examples/basic_movement.py

# Voice control
python src/voice/jetson_voice_server.py --language nl-NL
```

## Configuratie

### Robot Configuratie

Bewerk `config/robot_config.yaml`:

```yaml
robot:
  ip_address: "192.168.123.161"  # Pas aan indien nodig
  port: 8080
  timeout: 5.0
  network_interface: "eth0"       # Pas aan indien nodig
```

### Environment Variabelen

Bewerk `.env`:

```bash
GO2_ROBOT_IP=192.168.123.161
GO2_NETWORK_INTERFACE=eth0
JETSON_VOICE_SERVER_PORT=5000
JETSON_WHISPER_MODEL=base
JETSON_LANGUAGE=nl
```

## Script Opties

Het setup script ondersteunt opties:

```bash
# Skip Git clone (als je al een repository hebt)
bash scripts/setup_jetson_project.sh --skip-git

# Skip dependencies installatie (sneller, installeer later)
bash scripts/setup_jetson_project.sh --skip-deps

# Beide
bash scripts/setup_jetson_project.sh --skip-git --skip-deps
```

## Troubleshooting

### Probleem: Git Clone Faalt

**Oplossing:**
```bash
# Clone handmatig
cd ~
git clone https://github.com/Werkomgeving-van-de-Toekomst/robothond.git go2-ai
cd go2-ai
bash scripts/setup_jetson_project.sh --skip-git
```

### Probleem: Dependencies Installatie Faalt

**Oplossing:**
```bash
cd ~/go2-ai
source venv/bin/activate

# Installeer handmatig
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements_voice.txt
```

### Probleem: CycloneDDS Niet Geïnstalleerd

**Oplossing:**
```bash
# Compileer CycloneDDS eerst (zie docs/OFFICIELE_SDK_INTEGRATIE.md)
# Dan:
export CYCLONEDDS_HOME=/path/to/cyclonedds/install
pip install cyclonedds==0.10.2
```

### Probleem: Robot Niet Bereikbaar

**Oplossing:**
```bash
# Check netwerk configuratie
ip addr show eth0

# Test verbinding
ping 192.168.123.161

# Run netwerk setup opnieuw
sudo bash scripts/setup_jetson_go2.sh eth0
```

## Handige Aliassen

Na setup zijn deze aliassen beschikbaar (in nieuwe terminals):

```bash
go2-activate  # Activeer virtual environment
go2-cd        # Ga naar project directory
```

## Development Workflow

### 1. Code Ontwikkelen op PC

```bash
# Op je ontwikkel PC
cd ~/Projects/unitreego2
# ... maak wijzigingen ...
git add .
git commit -m "Mijn wijzigingen"
git push origin main
```

### 2. Sync naar Jetson

```bash
# Op Jetson
cd ~/go2-ai
git pull origin main
```

### 3. Test op Jetson

```bash
cd ~/go2-ai
source venv/bin/activate
python src/examples/diagnostics.py
```

## Zie Ook

- [JETSON_GO2_MONTAGE.md](JETSON_GO2_MONTAGE.md) - Hardware montage
- [JETSON_VOICE_PROCESSING.md](JETSON_VOICE_PROCESSING.md) - Voice setup
- [GO2_POWER_OUTLET.md](GO2_POWER_OUTLET.md) - Power setup
- [OFFICIELE_SDK_INTEGRATIE.md](OFFICIELE_SDK_INTEGRATIE.md) - SDK installatie

