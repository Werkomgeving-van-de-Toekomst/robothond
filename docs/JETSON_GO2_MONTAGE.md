# Jetson AGX Orin Montage op Go2 Robot

Deze handleiding beschrijft hoe je een Jetson AGX Orin op de Go2 robot monteert voor AI inference met directe Ethernet verbinding.

## Architectuur Overzicht

```
┌─────────────────────────────────────────────────────────────┐
│                        Je Netwerk                           │
│                                                             │
│   ┌─────────────┐         WiFi            ┌─────────────┐  │
│   │ Ontwikkel PC │◄─────────────────────►│   Router    │  │
│   └─────────────┘                         └──────┬──────┘  │
│                                                  │ WiFi    │
│                                                  ▼         │
│                                           ┌─────────────┐  │
│                                           │ Jetson AGX  │  │
│                                           │    Orin     │  │
│                                           │ WiFi: DHCP  │  │
│                                           │ eth0: .123.20│ │
│                                           └──────┬──────┘  │
│                                                  │ Ethernet│
│                                                  ▼         │
│                                           ┌─────────────┐  │
│                                           │  Go2 Robot  │  │
│                                           │.123.161     │  │
│                                           └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Go2 Payload Specificaties

Gebaseerd op [Unitree Go2 Payload documentatie](https://support.unitree.com/home/en/developer/Payload):

| Specificatie | Waarde |
|--------------|--------|
| **Max payload gewicht** | 8 kg (Go2 EDU) |
| **Aanbevolen payload** | < 5 kg voor optimale mobiliteit |
| **Montage oppervlak** | Rug van de robot |
| **Bevestigingspunten** | M3 schroefgaten in patroon |
| **Payload interface** | Ethernet + USB + GPIO beschikbaar |

### Jetson AGX Orin Specificaties

| Specificatie | Waarde |
|--------------|--------|
| **Afmetingen** | 110 x 110 x 71.65 mm |
| **Gewicht** | ~1.6 kg (met carrier board) |
| **Voeding** | 15-65W (afhankelijk van mode) |
| **Input voltage** | 9-20V DC of USB-C PD |

## 3D Print Mount Ontwerp

### Mount Specificaties

De mount is ontworpen voor:
- Stevige bevestiging op Go2 payload rails
- Goede ventilatie voor Jetson koeling
- Korte Ethernet kabel routing
- Optionele powerbank houder

### Bestand Locatie

```
hardware/
├── jetson_go2_mount/
│   ├── jetson_go2_mount.scad      # OpenSCAD bronbestand
│   ├── jetson_go2_mount.stl       # Print-ready STL
│   └── README.md                   # Print instructies
```

### Print Instellingen

| Parameter | Waarde |
|-----------|--------|
| **Materiaal** | PETG of ABS (sterker dan PLA) |
| **Layer hoogte** | 0.2 mm |
| **Infill** | 40-50% |
| **Supports** | Ja, voor overhangs |
| **Bed adhesion** | Brim aanbevolen |
| **Print tijd** | ~4-6 uur |

## Power Opties

### Optie 1: USB-C PD Powerbank (Aanbevolen)

De Jetson AGX Orin ondersteunt USB-C Power Delivery:

| Powerbank | Capaciteit | Output | Runtime |
|-----------|------------|--------|---------|
| Anker 737 | 24,000 mAh | 140W USB-C | ~3-4 uur |
| Omnicharge 20+ | 20,000 mAh | 100W USB-C | ~2-3 uur |
| BLUETTI AC2A | 204Wh | 300W AC | ~4-6 uur |

### Optie 2: Go2 Power Outlet (Aanbevolen voor lange sessies)

De Go2 heeft een **payload power outlet** die je kunt gebruiken met een DC-DC converter.

**Voordelen:**
- ✅ Onbeperkte runtime (zolang robot aan)
- ✅ Minder gewicht dan powerbank (~200g vs ~1kg)
- ✅ Geen opladen nodig

**Zie:** [GO2_POWER_OUTLET.md](GO2_POWER_OUTLET.md) voor complete instructies over:
- DC-DC converter selectie
- Aansluitinstructies
- Veiligheidsoverwegingen
- Troubleshooting

## Netwerk Configuratie

### Jetson Setup Script

```bash
#!/bin/bash
# setup_jetson_go2.sh

# Configureer Ethernet voor Go2
sudo nmcli con add type ethernet con-name go2-direct ifname eth0 \
    ipv4.addresses 192.168.123.20/24 \
    ipv4.method manual \
    ipv4.never-default true

# Activeer
sudo nmcli con up go2-direct

# Test
ping -c 2 192.168.123.161
```

### Routing

```bash
# Internet via WiFi, Robot via Ethernet
ip route
# default via 192.168.1.1 dev wlan0          <- Internet
# 192.168.123.0/24 dev eth0 proto kernel     <- Robot
```

## Development Workflow

1. **SSH naar Jetson** via WiFi vanaf je PC
2. **Code ontwikkelen** lokaal, sync via rsync/git
3. **AI inference** draait op Jetson GPU
4. **Robot commando's** via Ethernet naar Go2

```bash
# Sync code naar Jetson
rsync -avz ~/Projects/go2-ai/ jetson@<jetson-ip>:~/go2-ai/

# SSH en run
ssh jetson@<jetson-ip>
cd ~/go2-ai && python src/main.py
```

## Veiligheid

- **Gewicht**: Houd totaal payload onder 5 kg voor beste mobiliteit
- **Zwaartepunt**: Monteer zo laag mogelijk
- **Kabels**: Zorg dat kabels niet kunnen vastlopen in poten
- **Ventilatie**: Blokkeer Jetson ventilator niet

## Zie Ook

- [GO2_POWER_OUTLET.md](GO2_POWER_OUTLET.md) - **Power outlet setup** (aanbevolen!)
- [JETSON_AGX_ORIN_VERBINDING.md](JETSON_AGX_ORIN_VERBINDING.md) - Netwerk setup
- [JETSON_VOICE_PROCESSING.md](JETSON_VOICE_PROCESSING.md) - Voice AI setup
- [ETHERNET_VERBINDING.md](ETHERNET_VERBINDING.md) - Ethernet configuratie

