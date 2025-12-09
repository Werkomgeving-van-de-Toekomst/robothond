# Firewall Troubleshooting voor Go2 Robot

Complete guide voor firewall instellingen die de communicatie met de Go2 robot kunnen blokkeren.

## Overzicht

De Go2 robot gebruikt verschillende netwerk protocollen en poorten. Firewall instellingen kunnen deze communicatie blokkeren.

## Netwerk Protocollen en Poorten

### Custom Wrapper (Go2Robot)

- **Protocol**: UDP
- **Poort**: 8080
- **Richting**: Uitgaand (van computer naar robot)
- **IP Range**: 192.168.123.0/24 (lokaal netwerk)

### Officiële SDK (Go2RobotOfficial)

- **Protocol**: DDS (Data Distribution Service) via CycloneDDS
- **Poorten**: 
  - **7400-7500**: DDS discovery en communicatie
  - **Multicast**: 239.255.0.1 (standaard DDS multicast)
- **Richting**: Bidirectioneel (zowel inkomend als uitgaand)
- **IP Range**: 192.168.123.0/24 (lokaal netwerk)

## macOS Firewall Instellingen

### 1. macOS Firewall Controleren

```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Check of firewall aan staat
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate | grep "enabled"
```

### 2. macOS Firewall Uitschakelen (Tijdelijk voor Test)

```bash
# Schakel firewall uit (niet aanbevolen voor productie!)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# Schakel firewall weer aan
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
```

### 3. Python Toevoegen aan Firewall Uitzonderingen

```bash
# Voeg Python toe aan toegestane apps
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/bin/python3

# Of voor Homebrew Python
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /opt/homebrew/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /opt/homebrew/bin/python3

# Check of Python toegestaan is
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep python
```

### 4. Via System Preferences (GUI)

1. Open **System Preferences** (Systeemvoorkeuren)
2. Ga naar **Security & Privacy** (Beveiliging en privacy)
3. Klik op **Firewall** tab
4. Klik op het slot icoon om te ontgrendelen
5. Klik op **Firewall Options...** (Firewall opties...)
6. Voeg Python toe:
   - Klik op **+** (plus)
   - Navigeer naar Python executable:
     - `/usr/local/bin/python3` (standaard installatie)
     - `/opt/homebrew/bin/python3` (Homebrew op Apple Silicon)
     - Of je virtual environment Python: `venv/bin/python3`
   - Selecteer **Allow incoming connections** (Sta inkomende verbindingen toe)

### 5. Poort-specifieke Regels (Geavanceerd)

Voor meer controle kun je specifieke poorten openen:

```bash
# Open UDP poort 8080 (voor custom wrapper)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /System/Library/CoreServices/Applications/Network\ Utility.app
# Dit werkt niet direct, gebruik liever de GUI methode hierboven
```

**Let op**: macOS Firewall werkt op applicatie-niveau, niet op poort-niveau. Je moet Python toestaan, niet specifieke poorten.

## DDS (CycloneDDS) Firewall Instellingen

### 1. DDS Poorten Openen

DDS gebruikt een poort range voor discovery en communicatie:

```bash
# Check welke poorten DDS gebruikt
netstat -an | grep -E "7400|7500|239.255"

# Of tijdens robot verbinding:
lsof -i -P | grep -i python
```

### 2. Multicast Instellingen

DDS gebruikt multicast voor discovery. Zorg dat multicast niet geblokkeerd wordt:

```bash
# Check multicast routes
netstat -rn | grep 239.255

# Test multicast (als root)
ping -c 1 239.255.0.1
```

### 3. DDS Environment Variabelen

Zet deze environment variabelen voor DDS configuratie:

```bash
# In ~/.zshrc of ~/.bash_profile
export CYCLONEDDS_URI="<CycloneDDS config>"

# Of gebruik standaard instellingen (meestal niet nodig)
export CYCLONEDDS_URI="file:///path/to/config.xml"
```

## Linux Firewall (iptables/firewalld)

Als je Linux gebruikt:

### iptables

```bash
# Sta UDP poort 8080 toe
sudo iptables -A INPUT -p udp --dport 8080 -j ACCEPT
sudo iptables -A OUTPUT -p udp --dport 8080 -j ACCEPT

# Sta DDS poorten toe (7400-7500)
sudo iptables -A INPUT -p udp --dport 7400:7500 -j ACCEPT
sudo iptables -A OUTPUT -p udp --dport 7400:7500 -j ACCEPT

# Sta multicast toe
sudo iptables -A INPUT -d 239.255.0.1 -j ACCEPT
sudo iptables -A OUTPUT -d 239.255.0.1 -j ACCEPT

# Sla regels op (Ubuntu/Debian)
sudo iptables-save > /etc/iptables/rules.v4
```

### firewalld

```bash
# Sta UDP poort 8080 toe
sudo firewall-cmd --permanent --add-port=8080/udp
sudo firewall-cmd --reload

# Sta DDS poorten toe
sudo firewall-cmd --permanent --add-port=7400-7500/udp
sudo firewall-cmd --reload
```

## Windows Firewall

### Via GUI

1. Open **Windows Defender Firewall**
2. Klik op **Advanced settings**
3. Klik op **Inbound Rules** → **New Rule**
4. Selecteer **Port** → **Next**
5. Selecteer **UDP** en voer poort in: **8080**
6. Selecteer **Allow the connection**
7. Herhaal voor **Outbound Rules**

### Via PowerShell (Admin)

```powershell
# Sta UDP poort 8080 toe (inkomend)
New-NetFirewallRule -DisplayName "Go2 Robot UDP 8080" -Direction Inbound -Protocol UDP -LocalPort 8080 -Action Allow

# Sta UDP poort 8080 toe (uitgaand)
New-NetFirewallRule -DisplayName "Go2 Robot UDP 8080" -Direction Outbound -Protocol UDP -LocalPort 8080 -Action Allow

# Sta DDS poorten toe
New-NetFirewallRule -DisplayName "DDS Ports" -Direction Inbound -Protocol UDP -LocalPort 7400-7500 -Action Allow
New-NetFirewallRule -DisplayName "DDS Ports" -Direction Outbound -Protocol UDP -LocalPort 7400-7500 -Action Allow
```

## Testen van Firewall Instellingen

### 1. Test UDP Poort 8080

```bash
# Test uitgaande verbinding
nc -u -v 192.168.123.161 8080

# Of met Python
python -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b'test', ('192.168.123.161', 8080))
print('Verzonden')
"
```

### 2. Test DDS Communicatie

```bash
# Check DDS poorten tijdens verbinding
lsof -i -P | grep -E "7400|7500|python"

# Of gebruik netstat
netstat -an | grep -E "7400|7500"
```

### 3. Test met Diagnostiek Script

```bash
# Run diagnostiek script
python src/examples/diagnostics.py -i 192.168.123.161

# Run first time setup test
python src/examples/first_time_setup_test.py
```

## Veelvoorkomende Problemen

### Probleem 1: "Connection timeout" of "Connection refused"

**Oorzaak**: Firewall blokkeert uitgaande UDP verbindingen

**Oplossing**:
- Voeg Python toe aan macOS Firewall uitzonderingen
- Check of poort 8080 open is
- Test met `nc` of `telnet`

### Probleem 2: "DDS discovery failed"

**Oorzaak**: Firewall blokkeert DDS multicast of poorten 7400-7500

**Oplossing**:
- Sta multicast toe (239.255.0.1)
- Open poorten 7400-7500
- Check netwerk interface instellingen

### Probleem 3: "Robot niet gevonden" (officiële SDK)

**Oorzaak**: DDS discovery werkt niet door firewall

**Oplossing**:
- Zorg dat beide richtingen (inkomend/uitgaand) open zijn
- Check multicast instellingen
- Test met `ping 239.255.0.1`

### Probleem 4: Werkt op WiFi maar niet op Ethernet (of vice versa)

**Oorzaak**: Verschillende firewall regels per interface

**Oplossing**:
- Check firewall regels voor beide interfaces
- Test met beide verbindingen
- Zorg dat robot en computer opzelfde netwerk zitten

## Veiligheidsoverwegingen

### Best Practices

1. **Gebruik lokaal netwerk**: Robot moet op privé netwerk zitten (192.168.x.x)
2. **Beperk toegang**: Sta alleen verbindingen toe binnen lokaal netwerk
3. **Monitor verbindingen**: Check regelmatig welke apps verbinding maken
4. **Update regelmatig**: Houd firewall en systeem up-to-date

### Waarschuwingen

- ⚠️ **Schakel firewall niet permanent uit** - Dit maakt je systeem kwetsbaar
- ⚠️ **Gebruik geen publiek WiFi** - Robot communicatie is niet versleuteld
- ⚠️ **Beperk poorten** - Open alleen wat nodig is voor robot communicatie

## Automatische Firewall Test Script

Maak een test script om firewall instellingen te checken:

```python
#!/usr/bin/env python3
"""Test firewall instellingen voor Go2 robot"""

import socket
import sys

def test_udp_port(ip, port):
    """Test UDP poort verbinding"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        sock.sendto(b"test", (ip, port))
        print(f"✓ UDP {ip}:{port} - Verzonden")
        return True
    except Exception as e:
        print(f"❌ UDP {ip}:{port} - Fout: {e}")
        return False

def test_dds_ports():
    """Test DDS poorten"""
    ports = list(range(7400, 7501))
    print(f"Test DDS poorten 7400-7500...")
    # DDS gebruikt dynamische poorten, moeilijk te testen zonder actieve verbinding
    return True

if __name__ == "__main__":
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.123.161"
    
    print("Firewall Test voor Go2 Robot")
    print("=" * 50)
    
    # Test UDP 8080
    test_udp_port(robot_ip, 8080)
    
    # Test DDS (informatief)
    test_dds_ports()
    
    print("\n💡 Tip: Als tests falen, check firewall instellingen")
```

## Referenties

- [macOS Firewall Documentatie](https://support.apple.com/guide/mac-help/use-the-application-firewall-mh11783/mac)
- [CycloneDDS Documentatie](https://github.com/eclipse-cyclonedds/cyclonedds)
- [DDS Security](https://www.omg.org/spec/DDS-SECURITY/)

## Samenvatting

**Voor macOS (aanbevolen)**:
1. Open System Preferences → Security & Privacy → Firewall
2. Voeg Python toe aan toegestane apps
3. Sta inkomende verbindingen toe voor Python
4. Test met diagnostiek script

**Voor Linux**:
1. Open UDP poort 8080
2. Open DDS poorten 7400-7500
3. Sta multicast toe

**Voor Windows**:
1. Open Windows Defender Firewall
2. Maak regels voor UDP 8080 (inkomend/uitgaand)
3. Maak regels voor DDS poorten

Test altijd na het aanpassen van firewall instellingen!


