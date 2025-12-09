# Ethernet Verbinding Guide voor Go2 Robot

Complete guide voor het verbinden van de Go2 robot via Ethernet kabel direct naar je computer.

**Gebaseerd op officiële Unitree Go2 SDK instructies.**

## Overzicht

De Go2 robot kan via een Ethernet kabel direct verbonden worden met je computer. Dit is handig wanneer:
- WiFi problemen hebt
- Stabielere verbinding nodig hebt
- Robot niet op WiFi netwerk kan verbinden
- Je een directe verbinding wilt zonder router

## Vereisten

- **Ethernet kabel**: Standaard CAT5e of CAT6 Ethernet kabel
- **Go2 robot met Ethernet poort**: Check of jouw model een Ethernet poort heeft
- **Computer met Ethernet poort**: Of USB naar Ethernet adapter
- **Netwerk configuratie kennis**: Basis IP adres configuratie

## Stap 1: Fysieke Verbinding

### 1.1 Sluit Ethernet Kabel Aan

1. **Zoek Ethernet poort op robot**:
   - Meestal aan de achterkant of onderkant van de robot
   - Ziet eruit als een standaard RJ45 Ethernet poort
   - Mogelijk achter een deksel of flap

2. **Sluit één kant aan op robot**:
   - Steek Ethernet kabel in robot Ethernet poort
   - Zorg dat kabel goed vastzit (hoor "klik")

3. **Sluit andere kant aan op computer**:
   - Direct in Ethernet poort van computer, OF
   - Via USB naar Ethernet adapter

### 1.2 Check Verbinding

- **LED indicatoren**: Ethernet poort LED's moeten branden/knipperen
- **Robot**: Robot moet opgestart zijn
- **Computer**: Computer moet aan zijn

## Stap 2: Configureer Computer Netwerk Interface

### macOS: USB Ethernet Configuratie

#### Methode 1: Via System Preferences (GUI)

1. **Open System Preferences** → **Network**
2. **Zoek naar "USB 10/100/1000 LAN"** of "Ethernet" in linker menu
3. **Selecteer interface** (bijvoorbeeld "USB 10/100/1000 LAN")
4. **Configureer IPv4**:
   - Klik op **"Configure IPv4"** dropdown
   - Selecteer **"Manually"** (Handmatig)
5. **Voer IP adres in**:
   - **IP Address**: `192.168.123.222` (of ander adres in zelfde subnet, bijvoorbeeld 192.168.123.100)
   - **Subnet Mask**: `255.255.255.0`
   - **Router**: Laat leeg (geen router nodig voor directe verbinding)
6. **Klik op "Apply"**

#### Methode 2: Via Terminal (Command Line)

```bash
# Vind netwerk interface naam
networksetup -listallnetworkservices

# Configureer USB Ethernet (vervang "USB 10/100/1000 LAN" met jouw interface naam)
sudo networksetup -setmanual "USB 10/100/1000 LAN" 192.168.123.222 255.255.255.0

# Of als interface "en5" heet (check met ifconfig)
sudo ifconfig en5 192.168.123.222 netmask 255.255.255.0 up
```

**Vind Interface Naam voor 123 Subnet**:
```bash
# Toon alle netwerk interfaces
ifconfig

# Zoek naar interface met IP 192.168.123.x
# Bijvoorbeeld:
# enxf8e43b808e06: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
#         inet 192.168.123.222 netmask 0xffffff00 broadcast 192.168.123.255
# In dit geval is de interface naam: enxf8e43b808e06

# Of gebruik grep om alleen 123 subnet te tonen:
ifconfig | grep -B 1 "192.168.123"

# Of gebruik:
networksetup -listallhardwareports
```

**Belangrijk**: Noteer de interface naam die correspondeert met het 192.168.123 subnet. Deze naam heb je nodig als parameter bij het runnen van voorbeelden met de officiële SDK!

### Linux: USB Ethernet Configuratie

#### Methode 1: Via NetworkManager (GUI)

1. **Open Network Settings** (GNOME: Settings → Network)
2. **Zoek naar "Wired"** of "Ethernet" verbinding
3. **Klik op tandwiel icoon** (Settings)
4. **Ga naar IPv4 tab**
5. **Selecteer "Manual"**
6. **Voeg IP adres toe**:
   - **Address**: `192.168.123.222` (of ander adres in subnet)
   - **Netmask**: `255.255.255.0`
   - **Gateway**: Laat leeg
7. **Klik op "Apply"**

#### Methode 2: Via Terminal (Command Line)

```bash
# Vind netwerk interface naam
ip link show
# Of:
ifconfig -a

# Meestal "eth0", "eth1", "enp0s..." of "usb0" voor USB Ethernet

# Configureer statisch IP (vervang "eth0" met jouw interface)
sudo ip addr add 192.168.123.222/24 dev eth0
sudo ip link set eth0 up

# Of gebruik ifconfig (oudere distributies)
sudo ifconfig eth0 192.168.123.222 netmask 255.255.255.0 up
```

**Vind Interface Naam voor 123 Subnet**:
```bash
# Toon alle netwerk interfaces
ip addr show
# Of:
ifconfig

# Zoek naar interface met IP 192.168.123.x
# Bijvoorbeeld:
# 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
#     inet 192.168.123.222/24 brd 192.168.123.255 scope global eth0
# In dit geval is de interface naam: eth0

# Of gebruik grep:
ip addr show | grep -B 2 "192.168.123"
ifconfig | grep -B 1 "192.168.123"
```

**Belangrijk**: Noteer de interface naam die correspondeert met het 192.168.123 subnet. Deze naam heb je nodig als parameter bij het runnen van voorbeelden met de officiële SDK!

**Persistent Configuratie (NetworkManager)**:
```bash
# Via nmcli
sudo nmcli connection modify "Wired connection 1" \
    ipv4.addresses 192.168.123.100/24 \
    ipv4.method manual \
    ipv4.gateway ""

# Of via netplan (Ubuntu 18.04+)
sudo nano /etc/netplan/01-netcfg.yaml
```

**Netplan Configuratie** (`/etc/netplan/01-netcfg.yaml`):
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:  # Vervang met jouw interface naam
      addresses:
        - 192.168.123.222/24
      dhcp4: false
```

```bash
# Apply netplan configuratie
sudo netplan apply
```

### Windows: USB Ethernet Configuratie

#### Methode 1: Via Network Settings (GUI)

1. **Open Settings** → **Network & Internet** → **Ethernet**
2. **Klik op "Change adapter options"** (rechts)
3. **Rechtsklik op "Ethernet"** of "USB Ethernet Adapter"
4. **Selecteer "Properties"**
5. **Selecteer "Internet Protocol Version 4 (TCP/IPv4)"**
6. **Klik op "Properties"**
7. **Selecteer "Use the following IP address"**:
   - **IP address**: `192.168.123.222` (of ander adres in subnet)
   - **Subnet mask**: `255.255.255.0`
   - **Default gateway**: Laat leeg
8. **Klik op "OK"**

**Vind Interface Naam**:
```powershell
# Toon alle netwerk adapters
Get-NetAdapter

# Zoek adapter met IP 192.168.123.x
Get-NetIPAddress | Where-Object {$_.IPAddress -like "192.168.123.*"}

# Of gebruik ipconfig
ipconfig /all
# Zoek naar adapter met IP 192.168.123.222
```

**Belangrijk**: Noteer de interface naam (bijvoorbeeld "Ethernet" of "USB Ethernet Adapter"). Deze naam heb je mogelijk nodig als parameter bij het runnen van voorbeelden.

#### Methode 2: Via PowerShell (Command Line)

```powershell
# Vind netwerk interface naam
Get-NetAdapter

# Configureer statisch IP (vervang "Ethernet" met jouw interface naam)
New-NetIPAddress -InterfaceAlias "Ethernet" `
    -IPAddress 192.168.123.222 `
    -PrefixLength 24

# Of gebruik netsh (oudere Windows versies)
netsh interface ip set address "Ethernet" static 192.168.123.222 255.255.255.0
```

## Stap 3: Configureer Robot IP Adres

De Go2 robot heeft meestal een standaard IP adres voor directe Ethernet verbinding.

### Standaard Robot IP

- **Standaard IP**: `192.168.123.161`
- **Subnet**: `192.168.123.0/24`
- **Poort**: `8080` (UDP)

### Robot IP Configuratie (indien nodig)

Als je robot IP moet wijzigen:

#### Via Unitree Go App

1. **Verbind eerst via WiFi** met robot
2. **Open Unitree Go app**
3. **Ga naar Settings** → **Network Settings** → **Ethernet**
4. **Configureer IP adres**:
   - IP: `192.168.123.161` (of ander adres in subnet)
   - Subnet: `255.255.255.0`
5. **Save instellingen**

#### Via Web Interface

1. **Verbind eerst via WiFi** met robot
2. **Open browser**: `http://192.168.123.161`
3. **Login** (indien nodig)
4. **Ga naar Network Settings** → **Ethernet**
5. **Configureer IP adres**
6. **Save**

## Stap 4: Vind Netwerkkaart Naam (Belangrijk!)

Na het configureren van het IP adres, moet je de **netwerkkaart naam** vinden die correspondeert met het 192.168.123 subnet. Deze naam is nodig als parameter bij het runnen van voorbeelden met de officiële SDK.

### 4.1 Vind Netwerkkaart Naam

**macOS/Linux**:
```bash
# Toon alle netwerk interfaces
ifconfig

# Zoek naar interface met IP 192.168.123.x
# Bijvoorbeeld output:
# enxf8e43b808e06: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
#         inet 192.168.123.222 netmask 0xffffff00 broadcast 192.168.123.255
# 
# In dit geval is de netwerkkaart naam: enxf8e43b808e06

# Of gebruik grep om alleen 123 subnet te tonen:
ifconfig | grep -B 1 "192.168.123"
```

**Windows**:
```powershell
# Toon alle netwerk adapters
Get-NetAdapter

# Zoek adapter met IP 192.168.123.x
Get-NetIPAddress | Where-Object {$_.IPAddress -like "192.168.123.*"}

# Of gebruik ipconfig
ipconfig /all
```

**Voorbeeld Output (macOS)**:
```
enxf8e43b808e06: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
        options=4000<CHANNEL_IO>
        ether f8:e4:3b:80:8e:06
        inet 192.168.123.222 netmask 0xffffff00 broadcast 192.168.123.255
        media: autoselect (1000baseT <full-duplex>)
        status: active
```

In dit voorbeeld is de netwerkkaart naam: **`enxf8e43b808e06`**

**Noteer deze naam!** Je hebt deze nodig bij het runnen van voorbeelden:
```bash
# Officiële SDK voorbeeld
python unitree_sdk2_python/example/go2/high_level/go2_sport_client.py enxf8e43b808e06

# Of in Python code
from src.unitree_go2 import Go2RobotOfficial
robot = Go2RobotOfficial(
    ip_address="192.168.123.161",
    network_interface="enxf8e43b808e06"  # Jouw netwerkkaart naam
)
```

## Stap 5: Test Verbinding

### 5.1 Test Netwerk Verbinding

```bash
# Ping robot IP adres
ping 192.168.123.161

# Op macOS/Linux: Stop met Ctrl+C na enkele pings
# Op Windows: Stop automatisch na 4 pings
```

**Verwacht Resultaat**:
```
PING 192.168.123.161 (192.168.123.161): 56 data bytes
64 bytes from 192.168.123.161: icmp_seq=0 ttl=64 time=0.123 ms
64 bytes from 192.168.123.161: icmp_seq=1 ttl=64 time=0.098 ms
```

### 5.2 Test SDK Verbinding

```bash
# Test custom wrapper
python -c "
from src.unitree_go2 import Go2Robot
robot = Go2Robot(ip_address='192.168.123.161')
robot.connect()
print('✓ Verbinding succesvol!')
robot.disconnect()
"
```

### 5.3 Test Officiële SDK

```bash
# Test officiële SDK (als geïnstalleerd)
# Gebruik de netwerkkaart naam die je in stap 4 hebt gevonden
python -c "
from src.unitree_go2 import Go2RobotOfficial
robot = Go2RobotOfficial(
    ip_address='192.168.123.161',
    network_interface='enxf8e43b808e06'  # Vervang met jouw netwerkkaart naam!
)
robot.connect()
print('✓ Verbinding succesvol!')
robot.disconnect()
"
```

**Of gebruik officiële SDK voorbeelden direct**:
```bash
# Vervang 'enxf8e43b808e06' met jouw netwerkkaart naam
python unitree_sdk2_python/example/go2/high_level/go2_sport_client.py enxf8e43b808e06
```

### 5.4 Gebruik Diagnostiek Script

```bash
# Volledige diagnostiek
python src/examples/diagnostics.py -i 192.168.123.161
```

## Troubleshooting

### Probleem 1: Computer Ziet Ethernet Interface Niet

**Oplossingen**:

1. **Check USB adapter**:
   - Zorg dat USB naar Ethernet adapter correct aangesloten is
   - Probeer andere USB poort
   - Check of adapter werkt (test op andere computer)

2. **Installeer drivers**:
   - macOS: Meestal automatisch, check System Preferences → Network
   - Linux: Meestal automatisch, check `dmesg | grep -i usb`
   - Windows: Installeer drivers van adapter fabrikant

3. **Check interface status**:
   ```bash
   # macOS/Linux
   ifconfig
   ip link show
   
   # Windows
   ipconfig /all
   ```

### Probleem 2: Kan Niet Pingen naar Robot

**Mogelijke oorzaken**:
- Verkeerd IP adres geconfigureerd
- Robot niet opgestart
- Ethernet kabel defect
- Interface niet actief

**Oplossingen**:

1. **Check IP configuratie**:
   ```bash
   # macOS/Linux
   ifconfig
   ip addr show
   
   # Windows
   ipconfig
   ```

2. **Check robot status**:
   - Is robot aan?
   - Zie je LED indicatoren?
   - Check robot Ethernet poort LED's

3. **Test kabel**:
   - Probeer andere Ethernet kabel
   - Check beide uiteinden goed vastzitten

4. **Check interface status**:
   ```bash
   # macOS/Linux - Zet interface aan
   sudo ifconfig eth0 up
   sudo ip link set eth0 up
   
   # Windows - Enable interface
   netsh interface set interface "Ethernet" admin=enable
   ```

### Probleem 3: IP Conflict

**Symptomen**:
- Verbinding werkt niet
- Foutmelding over IP conflict

**Oplossingen**:

1. **Wijzig computer IP**:
   - Gebruik ander IP in subnet (bijvoorbeeld `192.168.123.100` → `192.168.123.101`)

2. **Check voor conflicten**:
   ```bash
   # macOS/Linux
   arp -a | grep 192.168.123
   
   # Windows
   arp -a | findstr 192.168.123
   ```

### Probleem 4: SDK Verbinding Werkt Niet

**Mogelijke oorzaken**:
- Firewall blokkeert poort 8080
- Verkeerd IP adres
- Robot niet in Ethernet modus

**Oplossingen**:

1. **Check firewall**:
   - Zie [Firewall Troubleshooting](./FIREWALL_TROUBLESHOOTING.md)
   - Sta UDP poort 8080 toe

2. **Check IP adres**:
   ```bash
   ping 192.168.123.161
   ```

3. **Test poort**:
   ```bash
   # macOS/Linux
   nc -u -v 192.168.123.161 8080
   
   # Of met Python
   python -c "
   import socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.sendto(b'test', ('192.168.123.161', 8080))
   print('Poort bereikbaar')
   "
   ```

### Probleem 5: Interface Naam Onbekend

**Vind Interface Naam**:

```bash
# macOS
networksetup -listallhardwareports
ifconfig | grep -E "^[a-z]"

# Linux
ip link show
ifconfig -a
ls /sys/class/net/

# Windows
Get-NetAdapter
ipconfig /all
```

**Veelvoorkomende Namen**:
- **macOS**: `en0`, `en1`, `en5`, `en6` (USB Ethernet)
- **Linux**: `eth0`, `eth1`, `enp0s...`, `usb0`
- **Windows**: `Ethernet`, `Ethernet 2`, `USB Ethernet Adapter`

## IP Adres Configuratie Overzicht

### Directe Verbinding (Geen Router)

Voor directe verbinding tussen robot en computer:

| Apparaat | IP Adres | Subnet Mask | Gateway |
|----------|----------|-------------|---------|
| **Robot** | `192.168.123.161` | `255.255.255.0` | - |
| **Computer** | `192.168.123.222` | `255.255.255.0` | - |

**Belangrijk**: 
- Beide apparaten moeten in hetzelfde subnet zitten (`192.168.123.0/24`)
- Geen gateway nodig (directe verbinding)
- Computer IP moet verschillen van robot IP
- **"222" kan gewijzigd worden** naar een ander nummer (bijvoorbeeld 100, 101, etc.), zolang het maar in het subnet `192.168.123.0/24` valt

### Via Router (Als Robot Aangesloten op Router)

Als robot via Ethernet op router is aangesloten:

| Apparaat | IP Adres | Subnet Mask | Gateway |
|----------|----------|-------------|---------|
| **Robot** | DHCP (bijvoorbeeld `192.168.1.100`) | `255.255.255.0` | Router IP |
| **Computer** | DHCP of Static | `255.255.255.0` | Router IP |

**Vind Robot IP**:
- Check router DHCP client list
- Of gebruik netwerk scan: `nmap -sn 192.168.1.0/24`

## Veelgestelde Vragen (FAQ)

### Q: Heb ik een cross-over kabel nodig?

**A**: Meestal niet. Moderne apparaten hebben Auto-MDIX en werken met standaard Ethernet kabels. Als directe verbinding niet werkt, probeer een cross-over kabel.

### Q: Kan ik internet hebben terwijl verbonden met robot?

**A**: Ja, maar je moet internet sharing configureren:
- **macOS**: System Preferences → Sharing → Internet Sharing
- **Linux**: Configureer NAT/forwarding
- **Windows**: Internet Connection Sharing

Of gebruik twee netwerk interfaces (WiFi voor internet, Ethernet voor robot).

### Q: Werkt dit met USB naar Ethernet adapter?

**A**: Ja, meestal wel. Zorg dat drivers geïnstalleerd zijn en interface correct geconfigureerd is.

### Q: Kan ik robot IP adres wijzigen?

**A**: Ja, via Unitree Go app of web interface. Zorg dat computer IP in hetzelfde subnet blijft.

### Q: Hoe snel is Ethernet verbinding?

**A**: Meestal 100 Mbps of 1 Gbps, afhankelijk van adapter en kabel. Veel sneller en stabieler dan WiFi.

### Q: Werkt dit zonder internet?

**A**: Ja, directe Ethernet verbinding werkt zonder internet. Alleen lokaal netwerk nodig.

## Alternatieve Configuraties

### Configuratie 1: Robot als DHCP Server

Sommige Go2 modellen kunnen als DHCP server fungeren:

1. **Configureer computer op DHCP** (automatisch IP)
2. **Robot geeft automatisch IP** aan computer
3. **Vind robot IP** via app of netwerk scan

### Configuratie 2: Via Switch of Hub

Als je meerdere apparaten wilt verbinden:

```
Robot ──┐
        ├── Switch/Hub ── Computer
PC 2 ───┘
```

- Alle apparaten in zelfde subnet
- Robot IP: `192.168.123.161`
- Computer IP: `192.168.123.222` (of ander nummer)
- PC 2 IP: `192.168.123.223` (of ander nummer)

## Referenties

- [WiFi Verbinding Guide](./WIFI_VERBINDING.md)
- [Firewall Troubleshooting](./FIREWALL_TROUBLESHOOTING.md)
- [First Time Setup](./FIRST_TIME_SETUP.md)
- [Go2 Handleiding](./GO2_HANDLEIDING.md)

## Samenvatting

**Snelle Setup**:

1. **Sluit Ethernet kabel aan** op robot en computer
2. **Configureer computer IP**: `192.168.123.222/24` (handmatig, "222" kan gewijzigd worden)
3. **Robot IP**: `192.168.123.161` (standaard)
4. **Vind netwerkkaart naam**: `ifconfig | grep -B 1 "192.168.123"` (noteer de naam!)
5. **Test verbinding**: `ping 192.168.123.161`
6. **Test SDK**: `python src/examples/diagnostics.py -i 192.168.123.161`
7. **Gebruik netwerkkaart naam** bij officiële SDK voorbeelden

**Belangrijk**: 
- Noteer de netwerkkaart naam die correspondeert met het 192.168.123 subnet
- Deze naam is nodig als parameter bij het runnen van officiële SDK voorbeelden
- Bijvoorbeeld: `python example.py enxf8e43b808e06` (vervang met jouw naam)

**Als het niet werkt**:
- Check IP configuratie (beide in zelfde subnet)
- Check interface status (moet "up" zijn)
- Test kabel (probeer andere kabel)
- Check firewall (poort 8080 UDP)
- Check of je de juiste netwerkkaart naam gebruikt

