#!/bin/bash
# =============================================================================
# Jetson AGX Orin + Go2 Robot Setup Script
# =============================================================================
#
# Dit script configureert een Jetson AGX Orin voor directe Ethernet verbinding
# met een Unitree Go2 robot.
#
# Gebruik: ./setup_jetson_go2.sh [eth_interface]
# Voorbeeld: ./setup_jetson_go2.sh eth0
#
# =============================================================================

set -e

# === CONFIGURATIE ===
ETH_INTERFACE="${1:-eth0}"
JETSON_IP="192.168.123.20"
ROBOT_IP="192.168.123.161"
SUBNET_MASK="24"
CONNECTION_NAME="go2-direct"

# Kleuren voor output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# === FUNCTIES ===

print_header() {
    echo ""
    echo -e "${BLUE}=========================================="
    echo "  Jetson AGX Orin + Go2 Setup"
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

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Dit script moet als root worden uitgevoerd"
        echo "Gebruik: sudo $0"
        exit 1
    fi
}

check_interface() {
    if ! ip link show "$ETH_INTERFACE" &>/dev/null; then
        print_error "Interface $ETH_INTERFACE bestaat niet!"
        echo ""
        echo "Beschikbare interfaces:"
        ip link show | grep -E "^[0-9]+:" | awk '{print "  - " $2}' | tr -d ':'
        exit 1
    fi
    print_success "Interface $ETH_INTERFACE gevonden"
}

configure_network() {
    print_info "Configureer netwerk verbinding..."
    
    # Verwijder bestaande configuratie indien aanwezig
    nmcli con delete "$CONNECTION_NAME" 2>/dev/null || true
    
    # Maak nieuwe verbinding
    nmcli con add type ethernet con-name "$CONNECTION_NAME" ifname "$ETH_INTERFACE" \
        ipv4.addresses "${JETSON_IP}/${SUBNET_MASK}" \
        ipv4.method manual \
        ipv4.never-default true \
        connection.autoconnect yes
    
    # Activeer verbinding
    nmcli con up "$CONNECTION_NAME"
    
    print_success "Netwerk geconfigureerd: $JETSON_IP op $ETH_INTERFACE"
}

test_robot_connection() {
    print_info "Test verbinding met robot..."
    
    if ping -c 2 -W 2 "$ROBOT_IP" > /dev/null 2>&1; then
        print_success "Robot bereikbaar op $ROBOT_IP"
        return 0
    else
        print_warning "Robot niet bereikbaar op $ROBOT_IP"
        echo ""
        echo "Controleer:"
        echo "  - Is de Ethernet kabel aangesloten?"
        echo "  - Is de robot aan?"
        echo "  - Is het robot IP correct? (standaard: 192.168.123.161)"
        return 1
    fi
}

install_dependencies() {
    print_info "Controleer dependencies..."
    
    # Check Python
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        print_success "Python gevonden: $PYTHON_VERSION"
    else
        print_error "Python3 niet gevonden"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &>/dev/null; then
        print_success "pip3 gevonden"
    else
        print_warning "pip3 niet gevonden, installeren..."
        apt-get update && apt-get install -y python3-pip
    fi
    
    # Check cyclonedds
    if python3 -c "import cyclonedds" 2>/dev/null; then
        print_success "CycloneDDS Python package gevonden"
    else
        print_warning "CycloneDDS niet gevonden"
        echo "  Installeer met: pip3 install cyclonedds"
    fi
}

setup_environment() {
    print_info "Setup environment variabelen..."
    
    # Maak environment file
    ENV_FILE="/etc/profile.d/go2_robot.sh"
    
    cat > "$ENV_FILE" << EOF
# Go2 Robot Environment Variables
export GO2_ROBOT_IP="$ROBOT_IP"
export GO2_NETWORK_INTERFACE="$ETH_INTERFACE"
export CYCLONEDDS_URI="file:///etc/cyclonedds/cyclonedds.xml"
EOF
    
    chmod +x "$ENV_FILE"
    print_success "Environment variabelen geconfigureerd in $ENV_FILE"
    
    # Maak CycloneDDS configuratie
    mkdir -p /etc/cyclonedds
    cat > /etc/cyclonedds/cyclonedds.xml << EOF
<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS xmlns="https://cdds.io/config">
    <Domain id="any">
        <General>
            <NetworkInterfaceAddress>$ETH_INTERFACE</NetworkInterfaceAddress>
        </General>
    </Domain>
</CycloneDDS>
EOF
    
    print_success "CycloneDDS configuratie aangemaakt"
}

show_status() {
    echo ""
    echo -e "${BLUE}=========================================="
    echo "  Netwerk Status"
    echo -e "==========================================${NC}"
    echo ""
    
    echo "WiFi:"
    WIFI_IP=$(ip -4 addr show wlan0 2>/dev/null | grep inet | awk '{print $2}' || echo "Niet verbonden")
    echo "  IP: $WIFI_IP"
    
    echo ""
    echo "Ethernet ($ETH_INTERFACE):"
    ETH_IP=$(ip -4 addr show "$ETH_INTERFACE" | grep inet | awk '{print $2}')
    echo "  IP: $ETH_IP"
    
    echo ""
    echo "Go2 Robot:"
    echo "  IP: $ROBOT_IP"
    
    echo ""
    echo "Routing:"
    ip route | head -5
}

show_next_steps() {
    echo ""
    echo -e "${BLUE}=========================================="
    echo "  Setup Voltooid!"
    echo -e "==========================================${NC}"
    echo ""
    echo "Volgende stappen:"
    echo ""
    echo "1. Source de environment variabelen:"
    echo "   source /etc/profile.d/go2_robot.sh"
    echo ""
    echo "2. Test de SDK verbinding:"
    echo "   python3 -c \""
    echo "   from unitree_sdk2py.core.channel import ChannelFactoryInitialize"
    echo "   ChannelFactoryInitialize(0, '$ETH_INTERFACE')"
    echo "   print('SDK OK')"
    echo "   \""
    echo ""
    echo "3. Run je AI applicatie:"
    echo "   python3 src/main.py --robot-ip $ROBOT_IP --interface $ETH_INTERFACE"
    echo ""
}

# === MAIN ===

print_header

echo "Configuratie:"
echo "  Ethernet interface: $ETH_INTERFACE"
echo "  Jetson IP: $JETSON_IP"
echo "  Robot IP: $ROBOT_IP"
echo ""

# Check root
check_root

# Check interface
check_interface

# Configure network
configure_network

# Test connection
test_robot_connection

# Install dependencies
install_dependencies

# Setup environment
setup_environment

# Show status
show_status

# Show next steps
show_next_steps

