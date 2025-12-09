#!/bin/bash
# Script om Ethernet interface te configureren voor Go2 robot verbinding
# Gebruik: ./configure_ethernet_macos.sh [interface_naam]
# Bijvoorbeeld: ./configure_ethernet_macos.sh en5

set -e

# Standaard interface als niet opgegeven
INTERFACE="${1:-en5}"
IP_ADDRESS="192.168.123.222"
SUBNET_MASK="255.255.255.0"
ROBOT_IP="192.168.123.161"

echo "=========================================="
echo "  Go2 Robot Ethernet Configuratie"
echo "=========================================="
echo ""
echo "Interface: $INTERFACE"
echo "IP Adres:  $IP_ADDRESS"
echo "Subnet:    $SUBNET_MASK"
echo "Robot IP:  $ROBOT_IP"
echo ""

# Check of interface bestaat
if ! ifconfig "$INTERFACE" &>/dev/null; then
    echo "❌ Fout: Interface $INTERFACE bestaat niet!"
    echo ""
    echo "Beschikbare interfaces:"
    ifconfig | grep "^en" | awk '{print "  - " $1}'
    exit 1
fi

# Check of al geconfigureerd
CURRENT_IP=$(ifconfig "$INTERFACE" | grep "inet " | awk '{print $2}' || echo "")
if [ "$CURRENT_IP" == "$IP_ADDRESS" ]; then
    echo "✓ Interface $INTERFACE heeft al IP $IP_ADDRESS geconfigureerd"
else
    echo "📡 Configureer interface $INTERFACE..."
    sudo ifconfig "$INTERFACE" "$IP_ADDRESS" netmask "$SUBNET_MASK" up
    
    if [ $? -eq 0 ]; then
        echo "✓ Interface succesvol geconfigureerd!"
    else
        echo "❌ Fout bij configureren van interface"
        exit 1
    fi
fi

echo ""
echo "📋 Huidige configuratie:"
ifconfig "$INTERFACE" | grep -E "flags|inet|ether" | head -3

echo ""
echo "🔍 Test verbinding met robot..."
if ping -c 2 -W 1000 "$ROBOT_IP" &>/dev/null; then
    echo "✓ Verbinding met robot succesvol!"
    echo ""
    echo "📝 Netwerkkaart naam voor SDK: $INTERFACE"
    echo ""
    echo "Gebruik deze naam bij SDK voorbeelden:"
    echo "  python unitree_sdk2_python/example/go2/high_level/go2_sport_client.py $INTERFACE"
    echo ""
    echo "Of in Python code:"
    echo "  robot = Go2RobotOfficial("
    echo "      ip_address='$ROBOT_IP',"
    echo "      network_interface='$INTERFACE'"
    echo "  )"
else
    echo "⚠️  Kan robot niet pingen"
    echo ""
    echo "Mogelijke oorzaken:"
    echo "  - Robot is niet aan"
    echo "  - Ethernet kabel niet aangesloten"
    echo "  - Robot IP is niet $ROBOT_IP"
    echo ""
    echo "Check verbinding en probeer opnieuw:"
    echo "  ping $ROBOT_IP"
fi

echo ""
echo "=========================================="

