#!/bin/bash
# =============================================================================
# Jetson AGX Orin Project Setup Script
# =============================================================================
#
# Dit script zet de complete projectstructuur op op de Jetson AGX Orin
# voor Go2 robot development met AI inference.
#
# Gebruik: ./setup_jetson_project.sh [--skip-git] [--skip-deps]
#
# =============================================================================

set -e

# === CONFIGURATIE ===
PROJECT_NAME="go2-ai"
PROJECT_DIR="$HOME/$PROJECT_NAME"
GIT_REPO_URL="https://github.com/Werkomgeving-van-de-Toekomst/robothond.git"
ROBOT_IP="192.168.123.161"
ETH_INTERFACE="eth0"

# Kleuren voor output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_GIT=false
SKIP_DEPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-git)
            SKIP_GIT=true
            shift
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        *)
            echo "Onbekend argument: $1"
            exit 1
            ;;
    esac
done

# === FUNCTIES ===

print_header() {
    echo ""
    echo -e "${BLUE}=========================================="
    echo "  Jetson AGX Orin Project Setup"
    echo -e "==========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_commands() {
    print_info "Check vereiste commando's..."
    
    local missing=()
    
    for cmd in git python3 pip3; do
        if ! command -v $cmd &>/dev/null; then
            missing+=($cmd)
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Ontbrekende commando's: ${missing[*]}"
        echo "Installeer met: sudo apt-get update && sudo apt-get install -y git python3 python3-pip"
        exit 1
    fi
    
    print_success "Alle vereiste commando's gevonden"
}

create_project_structure() {
    print_info "Maak projectstructuur aan..."
    
    # Hoofd directory
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Project directories
    mkdir -p src/{unitree_go2,voice,examples,simulation}
    mkdir -p config
    mkdir -p tests
    mkdir -p docs
    mkdir -p flows
    mkdir -p models/{whisper,yolo}
    mkdir -p logs
    mkdir -p scripts
    mkdir -p hardware
    
    print_success "Projectstructuur aangemaakt in $PROJECT_DIR"
}

clone_repository() {
    if [ "$SKIP_GIT" = true ]; then
        print_warning "Git clone overgeslagen (--skip-git)"
        return
    fi
    
    print_info "Clone repository..."
    
    cd "$PROJECT_DIR"
    
    if [ -d ".git" ]; then
        print_warning "Git repository bestaat al, pull updates..."
        git pull origin main
    else
        print_info "Clone van $GIT_REPO_URL..."
        git clone "$GIT_REPO_URL" .
    fi
    
    print_success "Repository gecloned/geupdate"
}

setup_python_environment() {
    print_info "Setup Python environment..."
    
    cd "$PROJECT_DIR"
    
    # Check Python versie
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_info "Python versie: $PYTHON_VERSION"
    
    # Maak virtual environment
    if [ ! -d "venv" ]; then
        print_info "Maak virtual environment aan..."
        python3 -m venv venv
    fi
    
    # Activeer venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_success "Python environment aangemaakt"
}

install_dependencies() {
    if [ "$SKIP_DEPS" = true ]; then
        print_warning "Dependencies installatie overgeslagen (--skip-deps)"
        return
    fi
    
    print_info "Installeer dependencies..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Basis dependencies
    if [ -f "requirements.txt" ]; then
        print_info "Installeer basis dependencies..."
        pip install -r requirements.txt
    fi
    
    # Voice dependencies
    if [ -f "requirements_voice.txt" ]; then
        print_info "Installeer voice dependencies..."
        pip install -r requirements_voice.txt
    fi
    
    # Jetson specifieke dependencies
    print_info "Installeer Jetson specifieke dependencies..."
    
    # CycloneDDS (als CYCLONEDDS_HOME gezet is)
    if [ -n "$CYCLONEDDS_HOME" ]; then
        pip install cyclonedds==0.10.2 || print_warning "CycloneDDS installatie mislukt (mogelijk niet gecompileerd)"
    else
        print_warning "CYCLONEDDS_HOME niet gezet - cyclonedds wordt niet geïnstalleerd"
    fi
    
    # Unitree SDK (als aanwezig)
    if [ -d "unitree_sdk2_python" ]; then
        print_info "Installeer Unitree SDK..."
        cd unitree_sdk2_python
        pip install -e . || print_warning "SDK installatie mislukt"
        cd ..
    fi
    
    print_success "Dependencies geïnstalleerd"
}

setup_network() {
    print_info "Configureer netwerk voor Go2 verbinding..."
    
    # Check of interface bestaat
    if ! ip link show "$ETH_INTERFACE" &>/dev/null; then
        print_warning "Interface $ETH_INTERFACE niet gevonden, skip netwerk configuratie"
        return
    fi
    
    # Run netwerk setup script als aanwezig
    if [ -f "scripts/setup_jetson_go2.sh" ]; then
        print_info "Run netwerk setup script..."
        sudo bash scripts/setup_jetson_go2.sh "$ETH_INTERFACE" || print_warning "Netwerk setup mislukt"
    else
        print_warning "Netwerk setup script niet gevonden"
    fi
}

create_config_files() {
    print_info "Maak configuratiebestanden aan..."
    
    cd "$PROJECT_DIR"
    
    # Robot config
    if [ ! -f "config/robot_config.yaml" ]; then
        cat > config/robot_config.yaml << EOF
# Go2 Robot Configuratie
robot:
  ip_address: "$ROBOT_IP"
  port: 8080
  timeout: 5.0
  network_interface: "$ETH_INTERFACE"

# Jetson Configuratie
jetson:
  voice_server:
    host: "0.0.0.0"
    port: 5000
    whisper_model: "base"
    language: "nl"
  
  ai_models:
    whisper_model_path: "models/whisper"
    yolo_model_path: "models/yolo"
EOF
        print_success "Robot config aangemaakt"
    fi
    
    # Environment file
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Go2 Robot Environment
GO2_ROBOT_IP=$ROBOT_IP
GO2_NETWORK_INTERFACE=$ETH_INTERFACE

# Jetson Configuratie
JETSON_VOICE_SERVER_PORT=5000
JETSON_WHISPER_MODEL=base
JETSON_LANGUAGE=nl

# CycloneDDS
CYCLONEDDS_URI=file:///etc/cyclonedds/cyclonedds.xml
EOF
        print_success "Environment file aangemaakt"
    fi
    
    # Shell profile update
    SHELL_PROFILE="$HOME/.bashrc"
    if ! grep -q "$PROJECT_DIR" "$SHELL_PROFILE"; then
        cat >> "$SHELL_PROFILE" << EOF

# Go2 AI Project
export GO2_PROJECT_DIR="$PROJECT_DIR"
alias go2-activate="source $PROJECT_DIR/venv/bin/activate"
alias go2-cd="cd $PROJECT_DIR"
EOF
        print_success "Shell profile bijgewerkt"
    fi
}

create_startup_scripts() {
    print_info "Maak startup scripts aan..."
    
    cd "$PROJECT_DIR/scripts"
    
    # Quick start script
    cat > start_voice_server.sh << 'EOF'
#!/bin/bash
# Start Jetson Voice Server

cd "$(dirname "$0")/.."
source venv/bin/activate

export GO2_ROBOT_IP="${GO2_ROBOT_IP:-192.168.123.161}"
export GO2_NETWORK_INTERFACE="${GO2_NETWORK_INTERFACE:-eth0}"

python src/voice/jetson_voice_server.py \
    --host 0.0.0.0 \
    --port 5000 \
    --robot-ip "$GO2_ROBOT_IP" \
    --interface "$GO2_NETWORK_INTERFACE" \
    --language nl-NL
EOF
    chmod +x start_voice_server.sh
    
    # Test script
    cat > test_connection.sh << 'EOF'
#!/bin/bash
# Test Go2 robot verbinding

cd "$(dirname "$0")/.."
source venv/bin/activate

export GO2_ROBOT_IP="${GO2_ROBOT_IP:-192.168.123.161}"
export GO2_NETWORK_INTERFACE="${GO2_NETWORK_INTERFACE:-eth0}"

echo "Test verbinding met robot op $GO2_ROBOT_IP..."
ping -c 3 "$GO2_ROBOT_IP" && echo "✓ Robot bereikbaar" || echo "✗ Robot niet bereikbaar"

echo ""
echo "Test SDK verbinding..."
python3 -c "
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
import os
interface = os.getenv('GO2_NETWORK_INTERFACE', 'eth0')
ChannelFactoryInitialize(0, interface)
print('✓ SDK geïnitialiseerd')
"
EOF
    chmod +x test_connection.sh
    
    print_success "Startup scripts aangemaakt"
}

show_summary() {
    echo ""
    echo -e "${BLUE}=========================================="
    echo "  Setup Voltooid!"
    echo -e "==========================================${NC}"
    echo ""
    echo "Project locatie: $PROJECT_DIR"
    echo ""
    echo "Volgende stappen:"
    echo ""
    echo "1. Activeer virtual environment:"
    echo "   source $PROJECT_DIR/venv/bin/activate"
    echo "   # Of gebruik: go2-activate"
    echo ""
    echo "2. Test verbinding met robot:"
    echo "   cd $PROJECT_DIR"
    echo "   ./scripts/test_connection.sh"
    echo ""
    echo "3. Start voice server:"
    echo "   ./scripts/start_voice_server.sh"
    echo ""
    echo "4. Of gebruik direct Python:"
    echo "   cd $PROJECT_DIR"
    echo "   source venv/bin/activate"
    echo "   python src/examples/diagnostics.py"
    echo ""
    echo "Handige aliassen (toegevoegd aan ~/.bashrc):"
    echo "  - go2-activate: Activeer virtual environment"
    echo "  - go2-cd: Ga naar project directory"
    echo ""
}

# === MAIN ===

print_header

echo "Configuratie:"
echo "  Project directory: $PROJECT_DIR"
echo "  Robot IP: $ROBOT_IP"
echo "  Ethernet interface: $ETH_INTERFACE"
echo ""

# Check commands
check_commands

# Create structure
create_project_structure

# Clone repository
clone_repository

# Setup Python
setup_python_environment

# Install dependencies
install_dependencies

# Setup network
setup_network

# Create config files
create_config_files

# Create startup scripts
create_startup_scripts

# Show summary
show_summary


