#!/bin/bash
# Script om Ethernet interface te configureren voor Go2 robot verbinding op Jetson AGX Orin
# Gebruik: ./configure_ethernet_jetson.sh [interface_naam] [verbinding_type]
# Bijvoorbeeld: ./configure_ethernet_jetson.sh eth0 direct
# Of: ./configure_ethernet_jetson.sh eth0 router

set -e

# Standaard waarden
INTERFACE="${1:-eth0}"
CONNECTION_TYPE="${2:-direct}"
IP_ADDRESS="192.168.123.222"
SUBNET_MASK="255.255.255.0"
ROBOT_IP="192.168.123.161"

echo "=========================================="
echo "  Go2 Robot Ethernet Configuratie"
echo "  Jetson AGX Orin"
echo "=========================================="
echo ""
echo "Interface: $INTERFACE"
echo "Type: $CONNECTION_TYPE"
echo "IP Adres:  $IP_ADDRESS"
echo "Subnet:    $SUBNET_MASK"
echo "Robot IP:  $ROBOT_IP"
echo ""

# Check of script als root draait
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Dit script moet als root/sudo uitgevoerd worden"
    echo "Gebruik: sudo $0 $INTERFACE $CONNECTION_TYPE"
    exit 1
fi

# Check of interface bestaat
if ! ip link show "$INTERFACE" &>/dev/null; then
    echo "❌ Fout: Interface $INTERFACE bestaat niet!"
    echo ""
    echo "Beschikbare interfaces:"
    ip link show | grep -E "^[0-9]+:" | awk '{print "  - " $2}' | sed 's/:$//'
    exit 1
fi

# Check of netplan beschikbaar is
if command -v netplan &> /dev/null; then
    echo "✓ Netplan gevonden - gebruik netplan configuratie"
    USE_NETPLAN=true
else
    echo "⚠️  Netplan niet gevonden - gebruik ifconfig (tijdelijk)"
    USE_NETPLAN=false
fi

if [ "$CONNECTION_TYPE" == "direct" ]; then
    echo ""
    echo "📡 Configureer voor DIRECTE verbinding..."
    
    if [ "$USE_NETPLAN" = true ]; then
        # Maak netplan configuratie
        NETPLAN_FILE="/etc/netplan/01-go2-robot.yaml"
        
        echo "Maak netplan configuratie: $NETPLAN_FILE"
        cat > "$NETPLAN_FILE" << EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: no
      addresses:
        - $IP_ADDRESS/24
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
EOF
        
        echo "✓ Netplan configuratie aangemaakt"
        echo ""
        echo "📋 Configuratie inhoud:"
        cat "$NETPLAN_FILE"
        echo ""
        
        echo "Apply netplan configuratie..."
        netplan apply
        
        echo "✓ Netplan configuratie toegepast!"
        
    else
        # Gebruik ifconfig (tijdelijk)
        echo "Configureer interface met ifconfig (tijdelijk)..."
        ifconfig "$INTERFACE" "$IP_ADDRESS" netmask "$SUBNET_MASK" up
        
        if [ $? -eq 0 ]; then
            echo "✓ Interface succesvol geconfigureerd!"
            echo "⚠️  Let op: Deze configuratie is tijdelijk en verdwijnt na reboot"
            echo "   Gebruik netplan voor permanente configuratie"
        else
            echo "❌ Fout bij configureren van interface"
            exit 1
        fi
    fi
    
elif [ "$CONNECTION_TYPE" == "router" ]; then
    echo ""
    echo "📡 Configureer voor ROUTER verbinding (DHCP)..."
    
    if [ "$USE_NETPLAN" = true ]; then
        # Maak netplan configuratie voor DHCP
        NETPLAN_FILE="/etc/netplan/01-go2-robot.yaml"
        
        echo "Maak netplan configuratie: $NETPLAN_FILE"
        cat > "$NETPLAN_FILE" << EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: yes
      dhcp6: no
EOF
        
        echo "✓ Netplan configuratie aangemaakt"
        echo ""
        echo "📋 Configuratie inhoud:"
        cat "$NETPLAN_FILE"
        echo ""
        
        echo "Apply netplan configuratie..."
        netplan apply
        
        echo "✓ Netplan configuratie toegepast!"
        echo ""
        echo "⚠️  Robot IP moet gevonden worden via router DHCP clients"
        echo "   Of via Unitree Go app"
        
    else
        echo "Configureer interface met DHCP..."
        dhclient "$INTERFACE"
        
        if [ $? -eq 0 ]; then
            echo "✓ Interface succesvol geconfigureerd met DHCP!"
        else
            echo "❌ Fout bij configureren van interface"
            exit 1
        fi
    fi
    
else
    echo "❌ Onbekend verbinding type: $CONNECTION_TYPE"
    echo "Gebruik: 'direct' of 'router'"
    exit 1
fi

echo ""
echo "📋 Huidige configuratie:"
ip addr show "$INTERFACE" | grep -E "inet|state" | head -2

echo ""
echo "🔍 Test verbinding met robot..."

if [ "$CONNECTION_TYPE" == "direct" ]; then
    if ping -c 2 -W 1000 "$ROBOT_IP" &>/dev/null; then
        echo "✓ Verbinding succesvol!"
        echo ""
        echo "Ping resultaten:"
        ping -c 3 "$ROBOT_IP"
    else
        echo "❌ Geen verbinding met robot"
        echo ""
        echo "Mogelijke oorzaken:"
        echo "  1. Ethernet kabel niet goed aangesloten"
        echo "  2. Robot is niet aan"
        echo "  3. Robot heeft ander IP adres"
        echo ""
        echo "Check fysieke verbinding en robot status"
        exit 1
    fi
else
    echo "⚠️  Test verbinding handmatig:"
    echo "  ping <robot-ip-adres>"
    echo ""
    echo "Vind robot IP via:"
    echo "  - Router web interface"
    echo "  - Unitree Go app"
    echo "  - Netwerk scan: nmap -sn 192.168.1.0/24"
fi

echo ""
echo "=========================================="
echo "  Configuratie Voltooid!"
echo "=========================================="
echo ""
echo "Interface naam voor SDK: $INTERFACE"
echo ""

if [ "$CONNECTION_TYPE" == "direct" ]; then
    echo "Gebruik bij SDK:"
    echo "  python3 unitree_sdk2_python/example/go2/high_level/go2_sport_client.py $INTERFACE"
    echo ""
    echo "Of in Python:"
    echo "  robot = Go2RobotOfficial("
    echo "      ip_address='$ROBOT_IP',"
    echo "      network_interface='$INTERFACE'"
    echo "  )"
else
    echo "Vind eerst robot IP adres, dan gebruik:"
    echo "  robot = Go2RobotOfficial("
    echo "      ip_address='<robot-ip>',"
    echo "      network_interface='$INTERFACE'"
    echo "  )"
fi

echo ""

