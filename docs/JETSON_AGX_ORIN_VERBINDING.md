# Jetson AGX Orin Verbinding met Go2 Robot

Complete guide voor het verbinden van een NVIDIA Jetson AGX Orin met de Unitree Go2 robot.

## Overzicht

De Jetson AGX Orin is een krachtige edge computing device die ideaal is voor:
- **Onboard AI processing**: Real-time computer vision, object detection
- **Edge computing**: Lokale AI inferentie zonder cloud
- **Autonome robotica**: Zelfstandige besluitvorming en controle
- **ROS2 integratie**: Robot Operating System 2 support

## Verbindingsopties

### Optie 1: Directe Ethernet Verbinding (Aanbevolen voor Development)

**Voordelen**:
- Laagste latency
- Meest stabiel
- Geen router nodig
- Ideaal voor real-time controle

**Configuratie**:
- Jetson IP: `192.168.123.222`
- Robot IP: `192.168.123.161`
- Subnet: `192.168.123.0/24`

### Optie 2: Via Router/Netwerk

**Voordelen**:
- Robot kan ook met andere apparaten communiceren
- Makkelijker voor meerdere ontwikkelaars
- WiFi beschikbaar voor robot

**Configuratie**:
- Beide apparaten opzelfde netwerk
- Robot krijgt IP via DHCP
- Jetson kan statisch of DHCP IP hebben

## Stap 1: Fysieke Verbinding

### Directe Ethernet Verbinding

1. **Sluit Ethernet kabel aan**:
   - Eén kant in Go2 robot Ethernet poort
   - Andere kant in Jetson AGX Orin Ethernet poort

2. **Check verbinding**:
   ```bash
   # Op Jetson
   ip link show
   # Zoek naar Ethernet interface (meestal eth0 of enp1s0)
   ```

### Via Router

1. **Sluit beide apparaten aan op router**:
   - Go2 robot via Ethernet naar router
   - Jetson AGX Orin via Ethernet naar router
   - Of gebruik WiFi voor één van beide

## Stap 2: Netwerk Configuratie op Jetson

### Methode 1: Via netplan (Ubuntu 20.04/22.04 - Aanbevolen)

#### Directe Ethernet Verbinding

1. **Vind netwerk interface naam**:
   ```bash
   ip link show
   # Of:
   ifconfig -a
   # Meestal: eth0, enp1s0, of eno1
   ```

2. **Maak/Edit netplan configuratie**:
   ```bash
   sudo nano /etc/netplan/01-netcfg.yaml
   ```

3. **Voor directe verbinding, gebruik deze configuratie**:
   ```yaml
   network:
     version: 2
     renderer: networkd
     ethernets:
       eth0:  # Vervang met jouw interface naam
         dhcp4: no
         addresses:
           - 192.168.123.222/24
         nameservers:
           addresses: [8.8.8.8, 8.8.4.4]
   ```

4. **Apply configuratie**:
   ```bash
   sudo netplan apply
   ```

5. **Check configuratie**:
   ```bash
   ip addr show eth0
   # Moet tonen: 192.168.123.222
   ```

#### Via Router (DHCP)

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: yes
      dhcp6: no
```

### Methode 2: Via NetworkManager (Als geïnstalleerd)

#### Via GUI (Desktop Ubuntu)

1. **Open Network Settings**:
   - Klik op netwerk icoon in systeem tray
   - Selecteer "Wired Settings" of "Network Settings"

2. **Configureer Ethernet**:
   - Selecteer Ethernet interface
   - Klik op settings (tandwiel icoon)
   - Ga naar "IPv4" tab
   - Kies "Manual"
   - Voeg toe:
     - Address: `192.168.123.222`
     - Netmask: `255.255.255.0`
     - Gateway: Laat leeg (voor directe verbinding)
   - Klik "Apply"

#### Via Command Line (nmcli)

```bash
# Vind interface naam
nmcli device status

# Configureer statisch IP (directe verbinding)
sudo nmcli connection modify "Wired connection 1" \
    ipv4.addresses 192.168.123.222/24 \
    ipv4.method manual

# Of voor DHCP (via router)
sudo nmcli connection modify "Wired connection 1" \
    ipv4.method auto

# Activeer verbinding
sudo nmcli connection up "Wired connection 1"
```

### Methode 3: Via ifconfig (Tijdelijk, voor testen)

```bash
# Configureer interface tijdelijk
sudo ifconfig eth0 192.168.123.222 netmask 255.255.255.0 up

# Check configuratie
ifconfig eth0

# Test verbinding
ping 192.168.123.161
```

**Let op**: Deze configuratie verdwijnt na reboot. Gebruik netplan voor permanente configuratie.

## Stap 3: Test Verbinding

### Ping Test

```bash
# Test verbinding met robot
ping -c 4 192.168.123.161

# Succesvolle output:
# PING 192.168.123.161 (192.168.123.161) 56(84) bytes of data.
# 64 bytes from 192.168.123.161: icmp_seq=1 ttl=64 time=0.123 ms
# 64 bytes from 192.168.123.161: icmp_seq=2 ttl=64 time=0.098 ms
```

### ARP Test

```bash
# Check of robot MAC adres bekend is
arp -a | grep 192.168.123.161

# Of:
ip neigh show | grep 192.168.123.161
```

### Poort Test

```bash
# Test UDP poort 8080 (voor custom SDK)
nc -u -v 192.168.123.161 8080

# Test DDS poorten (voor officiële SDK)
# DDS gebruikt poorten 7400-7500 en multicast
```

## Stap 4: Installeer Python SDK op Jetson

### Vereisten

```bash
# Update systeem
sudo apt update && sudo apt upgrade -y

# Installeer Python en pip
sudo apt install -y python3 python3-pip python3-venv

# Installeer build tools (voor CycloneDDS)
sudo apt install -y build-essential cmake git
sudo apt install -y libssl-dev libasio-dev
```

### Python Virtual Environment

```bash
# Maak virtual environment
python3 -m venv ~/go2_venv

# Activeer environment
source ~/go2_venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Installeer CycloneDDS (Voor Officiële SDK)

De Jetson AGX Orin heeft ARM64 architectuur, dus CycloneDDS moet gecompileerd worden:

```bash
# Installeer dependencies
sudo apt install -y \
    libcunit1-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    pkg-config \
    libevent-dev

# Clone CycloneDDS repository
cd ~
git clone https://github.com/eclipse-cyclonedds/cyclonedds.git
cd cyclonedds

# Build CycloneDDS
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
make -j$(nproc)
sudo make install

# Update library path
echo '/usr/local/lib' | sudo tee /etc/ld.so.conf.d/cyclonedds.conf
sudo ldconfig

# Set environment variable
echo 'export CYCLONEDDS_HOME=/usr/local' >> ~/.bashrc
source ~/.bashrc
```

### Installeer Unitree SDK

```bash
# Als je de officiële SDK hebt gekloond
cd ~/unitree_sdk2_python  # Of waar je SDK hebt geplaatst

# Installeer dependencies
pip install -r requirements.txt

# Installeer cyclonedds Python package
pip install cyclonedds

# Test installatie
python3 -c "import cyclonedds; print('CycloneDDS OK')"
```

### Installeer Custom SDK (Als je die gebruikt)

```bash
# Navigeer naar project directory
cd ~/unitreego2  # Of waar je project staat

# Installeer dependencies
pip install -r requirements.txt

# Test import
python3 -c "from src.unitree_go2 import Go2Robot; print('SDK OK')"
```

## Stap 5: Test SDK Verbinding

### Test Custom SDK

```python
#!/usr/bin/env python3
"""Test Go2 verbinding vanaf Jetson"""

from src.unitree_go2 import Go2Robot
import time

# Maak robot instance
robot = Go2Robot(ip_address="192.168.123.161")

# Test verbinding
print("Test verbinding...")
try:
    robot.connect()
    print("✓ Verbonden met robot!")
    
    # Test stand commando
    print("Test stand...")
    robot.stand()
    time.sleep(2)
    
    # Test sit commando
    print("Test sit...")
    robot.sit()
    time.sleep(2)
    
    robot.disconnect()
    print("✓ Test voltooid!")
    
except Exception as e:
    print(f"❌ Fout: {e}")
```

### Test Officiële SDK

```python
#!/usr/bin/env python3
"""Test officiële SDK verbinding vanaf Jetson"""

from src.unitree_go2 import Go2RobotOfficial
import time

# Maak robot instance
robot = Go2RobotOfficial(
    ip_address="192.168.123.161",
    network_interface="eth0"  # Vervang met jouw interface naam
)

# Test verbinding
print("Test verbinding...")
try:
    robot.connect()
    print("✓ Verbonden met robot!")
    
    # Test stand commando
    print("Test stand...")
    robot.stand()
    time.sleep(2)
    
    # Test sit commando
    print("Test sit...")
    robot.sit()
    time.sleep(2)
    
    robot.disconnect()
    print("✓ Test voltooid!")
    
except Exception as e:
    print(f"❌ Fout: {e}")
```

## Stap 6: Vind Netwerk Interface Naam voor SDK

De officiële SDK vereist de netwerk interface naam als parameter:

```bash
# Vind interface naam
ip link show

# Of:
ifconfig -a

# Meestal:
# - eth0 (standaard Ethernet)
# - enp1s0 (PCIe Ethernet)
# - eno1 (onboard Ethernet)

# Test welke interface verbonden is
ip addr show | grep "inet 192.168.123"
```

Gebruik deze naam bij SDK initialisatie:

```python
robot = Go2RobotOfficial(
    ip_address="192.168.123.161",
    network_interface="eth0"  # Jouw interface naam
)
```

## Use Cases voor Jetson AGX Orin

### 1. Real-time Computer Vision

```python
#!/usr/bin/env python3
"""Computer vision met Jetson en Go2"""

import cv2
from src.unitree_go2 import Go2RobotOfficial
import numpy as np

# Initialiseer robot
robot = Go2RobotOfficial(
    ip_address="192.168.123.161",
    network_interface="eth0"
)

# Initialiseer camera (als je camera op Jetson hebt)
cap = cv2.VideoCapture(0)

robot.connect()

try:
    while True:
        # Lees camera frame
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Voer object detection uit (bijvoorbeeld met YOLO)
        # ... AI processing ...
        
        # Stuur robot commando's gebaseerd op detectie
        # robot.move(forward=0.1, ...)
        
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
finally:
    cap.release()
    cv2.destroyAllWindows()
    robot.disconnect()
```

### 2. ROS2 Integratie

```bash
# Installeer ROS2 (bijvoorbeeld Humble)
# Zie: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html

# Maak ROS2 workspace
mkdir -p ~/go2_ros2_ws/src
cd ~/go2_ros2_ws/src

# Clone Unitree ROS2 packages (als beschikbaar)
# git clone <unitree-ros2-repo>

# Build workspace
cd ~/go2_ros2_ws
colcon build
source install/setup.bash
```

### 3. Edge AI Inferentie

```python
#!/usr/bin/env python3
"""Edge AI met TensorRT op Jetson"""

import tensorrt as trt
from src.unitree_go2 import Go2RobotOfficial

# Laad TensorRT engine (geoptimaliseerd voor Jetson)
# ... AI model loading ...

robot = Go2RobotOfficial(
    ip_address="192.168.123.161",
    network_interface="eth0"
)

robot.connect()

# Real-time AI inferentie en robot controle
# ...
```

## Troubleshooting

### Probleem: Interface niet gevonden

```bash
# Check alle interfaces
ip link show

# Check welke interface actief is
ip addr show

# Check netwerk status
sudo systemctl status NetworkManager
# Of:
sudo systemctl status systemd-networkd
```

### Probleem: Geen verbinding met robot

1. **Check fysieke verbinding**:
   ```bash
   # Check link status
   ethtool eth0  # Als ethtool geïnstalleerd is
   # Of:
   ip link show eth0
   # Moet "state UP" tonen
   ```

2. **Check IP configuratie**:
   ```bash
   ip addr show eth0
   # Moet 192.168.123.222 tonen voor directe verbinding
   ```

3. **Check firewall**:
   ```bash
   # Check firewall status
   sudo ufw status
   
   # Sta UDP poorten toe
   sudo ufw allow 8080/udp  # Voor custom SDK
   sudo ufw allow 7400:7500/udp  # Voor DDS
   ```

4. **Test met ping**:
   ```bash
   ping -c 4 192.168.123.161
   ```

### Probleem: CycloneDDS compileert niet

```bash
# Check compiler versie
gcc --version

# Installeer extra dependencies
sudo apt install -y \
    libcunit1-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    pkg-config \
    libevent-dev \
    libicu-dev

# Probeer opnieuw te compileren
cd ~/cyclonedds/build
rm -rf *
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
make -j$(nproc)
```

### Probleem: SDK kan niet verbinden

1. **Check robot IP**:
   ```bash
   ping 192.168.123.161
   ```

2. **Check interface naam**:
   ```bash
   ip link show
   # Gebruik exacte naam (bijvoorbeeld eth0, niet eth)
   ```

3. **Check DDS configuratie** (voor officiële SDK):
   ```bash
   # Check CYCLONEDDS_HOME
   echo $CYCLONEDDS_HOME
   
   # Check library path
   ldconfig -p | grep cyclonedds
   ```

4. **Test met officiële voorbeeld**:
   ```bash
   cd ~/unitree_sdk2_python/example/go2/high_level
   python3 go2_sport_client.py eth0
   ```

### Probleem: Hoge latency

Voor real-time toepassingen:

1. **Gebruik directe Ethernet verbinding** (niet via router)
2. **Disable power management**:
   ```bash
   # Check power management
   cat /sys/class/net/eth0/power/control
   
   # Disable (als mogelijk)
   echo "on" | sudo tee /sys/class/net/eth0/power/control
   ```

3. **Set CPU governor naar performance**:
   ```bash
   # Check current governor
   cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   
   # Set naar performance (als jetson_clocks niet actief is)
   sudo nvpmodel -m 0  # Max performance mode
   sudo jetson_clocks  # Max clock speeds
   ```

## Performance Optimalisatie

### Jetson Power Modes

```bash
# Check huidige power mode
sudo nvpmodel -q

# Set naar max performance
sudo nvpmodel -m 0
sudo jetson_clocks

# Check GPU/CPU status
sudo tegrastats
```

### Network Optimalisatie

```bash
# Increase network buffer sizes
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728

# Make permanent
echo "net.core.rmem_max=134217728" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max=134217728" | sudo tee -a /etc/sysctl.conf
```

## Samenvatting

### Quick Start Checklist

- [ ] Ethernet kabel aangesloten (direct of via router)
- [ ] Netwerk interface geconfigureerd (192.168.123.222 voor direct)
- [ ] Verbinding getest met `ping 192.168.123.161`
- [ ] Python environment aangemaakt en geactiveerd
- [ ] CycloneDDS gecompileerd en geïnstalleerd (voor officiële SDK)
- [ ] Unitree SDK geïnstalleerd
- [ ] Test script uitgevoerd en succesvol
- [ ] Interface naam genoteerd voor SDK gebruik

### Belangrijke Commando's

```bash
# Netwerk configuratie
ip link show                    # Vind interface naam
sudo netplan apply              # Apply netplan config
ping 192.168.123.161           # Test verbinding

# SDK test
python3 test_connection.py      # Test robot verbinding

# Performance
sudo jetson_clocks             # Max performance
sudo tegrastats                 # Monitor status
```

## Referenties

- [Unitree Go2 SDK Documentatie](./GO2_SDK_REFERENTIE.md)
- [Ethernet Verbinding Guide](./ETHERNET_VERBINDING.md)
- [NVIDIA Jetson Developer Guide](https://developer.nvidia.com/embedded/jetson-agx-orin)
- [CycloneDDS Documentatie](https://github.com/eclipse-cyclonedds/cyclonedds)

