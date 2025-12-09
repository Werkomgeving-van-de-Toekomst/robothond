# Jetson-Robot Verbinding voor Multi-Jetson Setup

Complete guide voor het verbinden van meerdere Jetsons met één Go2 robot.

## Overzicht

Bij multi-Jetson setup moeten beide Jetsons verbinden met dezelfde robot. Dit document legt uit hoe dit werkt en hoe conflicten voorkomen worden.

## Netwerk Architectuur

### Directe Ethernet Verbinding

```
                    ┌─────────────┐
                    │  Go2 Robot  │
                    │192.168.123.161│
                    └──────┬───────┘
                           │
                           │ Ethernet (192.168.123.0/24)
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │ Jetson 1  │  │ Jetson 2  │  │  Load     │
    │eth0       │  │eth0       │  │  Balancer  │
    │192.168.   │  │192.168.   │  │  (optioneel)│
    │123.222    │  │123.223    │  │            │
    └───────────┘  └───────────┘  └───────────┘
```

### Via Router

```
                    ┌─────────────┐
                    │   Router    │
                    │ 192.168.1.1 │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │  Go2 Robot│  │ Jetson 1  │  │ Jetson 2  │
    │192.168.1.100│ │192.168.1.101│ │192.168.1.102│
    └───────────┘  └───────────┘  └───────────┘
```

## Stap-voor-Stap Configuratie

### Stap 1: Netwerk Configuratie op Jetson 1

```bash
# Vind netwerk interface naam
ip link show  # Meestal eth0

# Configureer IP adres (directe verbinding)
sudo ifconfig eth0 192.168.123.222 netmask 255.255.255.0 up

# Of via netplan (permanent)
sudo nano /etc/netplan/01-jetson1.yaml
```

Netplan configuratie:
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.123.222/24
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

```bash
sudo netplan apply
```

### Stap 2: Netwerk Configuratie op Jetson 2

```bash
# Configureer IP adres (ANDER IP dan Jetson 1!)
sudo ifconfig eth0 192.168.123.223 netmask 255.255.255.0 up

# Of via netplan
sudo nano /etc/netplan/01-jetson2.yaml
```

Netplan configuratie:
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.123.223/24  # ANDER IP!
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

```bash
sudo netplan apply
```

### Stap 3: Test Verbinding met Robot

**Op beide Jetsons**:

```bash
# Test ping
ping -c 4 192.168.123.161

# Test SDK verbinding
python3 -c "
from src.unitree_go2 import Go2RobotOfficial
robot = Go2RobotOfficial(
    ip_address='192.168.123.161',
    network_interface='eth0'
)
robot.connect()
print('✓ Verbonden met robot!')
robot.stand()
import time
time.sleep(2)
robot.sit()
robot.disconnect()
"
```

### Stap 4: Start Voice Servers op Beide Jetsons

**Jetson 1**:
```bash
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --port 8888 \
    --whisper-model medium \
    --language nl-NL
```

**Jetson 2**:
```bash
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --port 8888 \
    --whisper-model medium \
    --language nl-NL
```

**Belangrijk**:
- Beide gebruiken **dezelfde robot IP** (`192.168.123.161`)
- Beide gebruiken **dezelfde netwerk interface** (`eth0`)
- Beide gebruiken **dezelfde poort** (`8888`) - dit is OK omdat ze verschillende IP's hebben

### Stap 5: Start Load Balancer

```bash
# Op aparte computer of één van de Jetsons
python3 src/voice/multi_jetson_loadbalancer.py \
    --jetson-servers http://192.168.123.222:8888 http://192.168.123.223:8888 \
    --strategy round-robin \
    --port 8889
```

## Hoe Werkt Het?

### Commando Flow

```
1. Client → Load Balancer (http://192.168.123.222:8889)
   POST /api/voice/listen {"text": "sta op"}

2. Load Balancer → Kiest Jetson (bijv. Jetson 1)
   POST http://192.168.123.222:8888/api/voice/listen

3. Jetson 1 → Verwerkt spraak (Whisper)
   → Herkent: "sta op"
   → Retourneert: {"status": "ok", "recognized": "sta op"}

4. Load Balancer → Ontvangt resultaat
   → Stuurt commando naar robot (via eigen verbinding)
   → Retourneert resultaat naar client
```

### Waarom Load Balancer?

**Probleem zonder load balancer**:
- Beide Jetsons kunnen tegelijk commando's sturen
- Conflicten mogelijk (bijv. "sta op" en "ga zitten" tegelijk)
- Robot kan verward raken

**Oplossing met load balancer**:
- Load balancer coördineert alle commando's
- Commando's worden sequentieel verwerkt
- Geen conflicten

## Belangrijke Configuratie Details

### IP Adres Verdeling

| Apparaat | IP Adres | Interface | Opmerking |
|----------|----------|-----------|-----------|
| Go2 Robot | `192.168.123.161` | eth0 | Standaard robot IP |
| Jetson 1 | `192.168.123.222` | eth0 | Eerste Jetson |
| Jetson 2 | `192.168.123.223` | eth0 | Tweede Jetson (ander IP!) |
| Load Balancer | `192.168.123.224` | eth0 | Optioneel (kan op Jetson draaien) |

### Poorten

| Service | Poort | Opmerking |
|---------|-------|-----------|
| Jetson Voice Server | `8888` | Beide Jetsons (verschillende IP's) |
| Load Balancer | `8889` | Coördineert commando's |
| Robot DDS | `7400-7500` | Automatisch door SDK |

## Troubleshooting

### Probleem: Jetson 2 kan niet verbinden

**Check**:
```bash
# Check IP configuratie
ip addr show eth0

# Moet tonen: 192.168.123.223 (niet hetzelfde als Jetson 1!)

# Check verbinding
ping 192.168.123.161

# Check of poort niet in gebruik is
netstat -tuln | grep 8888
```

### Probleem: Beide Jetsons kunnen robot niet bereiken

**Oplossing**:
```bash
# Check robot IP
ping 192.168.123.161

# Check netwerk interface
ip link show eth0  # Moet "state UP" tonen

# Check routing
ip route show

# Test met SDK
python3 -c "
from src.unitree_go2 import Go2RobotOfficial
robot = Go2RobotOfficial(ip_address='192.168.123.161', network_interface='eth0')
robot.connect()
"
```

### Probleem: Commando conflicten

**Oplossing**:
- Zorg dat load balancer gebruikt wordt
- Gebruik niet beide Jetsons direct voor robot commando's
- Load balancer zorgt voor sequentiële verwerking

## Best Practices

### 1. Gebruik Load Balancer Altijd

✅ **Goed**:
```
Client → Load Balancer → Jetson → Load Balancer → Robot
```

❌ **Fout**:
```
Client → Jetson 1 → Robot
Client → Jetson 2 → Robot  (Conflicten!)
```

### 2. Verschillende IP's voor Jetsons

- Jetson 1: `192.168.123.222`
- Jetson 2: `192.168.123.223`
- **Nooit hetzelfde IP!**

### 3. Test Individueel Eerst

```bash
# Test Jetson 1 alleen
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.123.222:8888 \
    --command "sta op"

# Test Jetson 2 alleen
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.123.223:8888 \
    --command "ga zitten"

# Test via load balancer
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.123.222:8889 \
    --command "stop"
```

## Samenvatting

### Checklist

- [ ] Jetson 1 geconfigureerd met IP `192.168.123.222`
- [ ] Jetson 2 geconfigureerd met IP `192.168.123.223` (ander IP!)
- [ ] Beide Jetsons kunnen robot pingen (`192.168.123.161`)
- [ ] Beide Jetsons kunnen SDK verbinding maken
- [ ] Voice servers gestart op beide Jetsons (poort 8888)
- [ ] Load balancer gestart met beide Jetson URLs
- [ ] Clients gebruiken load balancer (niet individuele Jetsons)

### Quick Reference

```bash
# Jetson 1 configuratie
sudo ifconfig eth0 192.168.123.222 netmask 255.255.255.0 up
python3 src/voice/jetson_voice_server.py --robot-ip 192.168.123.161 --network-interface eth0 --port 8888

# Jetson 2 configuratie
sudo ifconfig eth0 192.168.123.223 netmask 255.255.255.0 up
python3 src/voice/jetson_voice_server.py --robot-ip 192.168.123.161 --network-interface eth0 --port 8888

# Load balancer
python3 src/voice/multi_jetson_loadbalancer.py \
    --jetson-servers http://192.168.123.222:8888 http://192.168.123.223:8888
```

## Referenties

- [Multi-Jetson Setup](./MULTI_JETSON_SETUP.md) - Complete multi-Jetson guide
- [Jetson AGX Orin Verbinding](./JETSON_AGX_ORIN_VERBINDING.md) - Basis Jetson verbinding
- [Ethernet Verbinding](./ETHERNET_VERBINDING.md) - Robot netwerk configuratie

