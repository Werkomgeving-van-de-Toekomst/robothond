# USB WiFi Dongle Setup voor Go2 Robot

Complete guide voor het installeren en configureren van een USB WiFi dongle op de Go2 robot voor wireless programmeren.

## Overzicht

Als de ingebouwde WiFi van de Go2 niet werkt of je een betere WiFi dongle wilt gebruiken, kun je een externe USB WiFi dongle aansluiten. Deze guide legt uit hoe je dit installeert en configureert.

## Vereisten

- **USB WiFi Dongle**: Compatibel met Linux (ARM architecture)
- **Go2 Robot**: Met USB poort beschikbaar
- **SSH Toegang**: Tot de Go2 robot (of directe toegang)
- **Basis Linux kennis**: Command line gebruik

## Stap 1: Locatie USB Poort op Go2

### Waar Zit de USB Poort?

De Go2 robot heeft meestal **één of meer USB poorten** op verschillende locaties:

1. **Achterkant van de robot** (meestal):
   - Onder het deksel aan de achterkant
   - Mogelijk achter een rubberen flap
   - Type-A USB poort

2. **Onderkant van de robot**:
   - Soms onder een deksel
   - Check handleiding voor exacte locatie

3. **Zijkant** (afhankelijk van model):
   - Sommige modellen hebben USB aan de zijkant

### Hoe Vind Je de USB Poort?

1. **Check visueel**: Zoek naar USB-A poort (rechthoekige poort)
2. **Check handleiding**: Unitree Go2 handleiding heeft meestal diagram
3. **Check LED indicatoren**: USB poorten hebben soms LED's die oplichten

### Belangrijk

- **Zorg dat robot UIT staat** voordat je USB dongle aansluit (aanbevolen)
- **Gebruik korte USB kabel** of directe aansluiting (minder kans op losraken)
- **Check compatibiliteit**: WiFi dongle moet Linux/ARM ondersteunen

## Stap 2: Sluit USB WiFi Dongle Aan

### 2.1 Fysieke Aansluiting

1. **Zet robot UIT** (aanbevolen voor veiligheid)
2. **Sluit USB WiFi dongle aan** in USB poort
3. **Zorg dat dongle goed vastzit** (niet los kan raken tijdens beweging)
4. **Zet robot AAN**
5. **Wacht tot robot volledig opgestart is** (30-60 seconden)

### 2.2 Check of Dongle Herkend Wordt

**Via SSH** (als beschikbaar):
```bash
# Verbind met robot via SSH
ssh unitree@192.168.123.161
# Of:
ssh root@192.168.123.161

# Check USB devices
lsusb

# Je zou je WiFi dongle moeten zien, bijvoorbeeld:
# Bus 001 Device 003: ID 0bda:8179 Realtek Semiconductor Corp. RTL8188EUS 802.11n Wireless Network Adapter
```

**Via Directe Toegang** (als robot lokaal toegankelijk is):
- Gebruik dezelfde commando's op de robot zelf

## Stap 3: Check WiFi Dongle Detectie

### 3.1 Check Netwerk Interfaces

```bash
# Check alle netwerk interfaces
ip link show

# Of:
ifconfig -a

# Je zou een nieuwe interface moeten zien, bijvoorbeeld:
# wlan1, wlan2, wlx... (afhankelijk van dongle)
```

### 3.2 Check WiFi Driver Status

```bash
# Check of WiFi driver geladen is
lsmod | grep -i wifi
lsmod | grep -i 80211
lsmod | grep -i rtl  # Voor Realtek dongles

# Check dmesg voor USB/WiFi berichten
dmesg | tail -20
dmesg | grep -i usb
dmesg | grep -i wifi
```

### 3.3 Probleem: Dongle Niet Herkend

**Mogelijke oorzaken**:
- Driver niet geïnstalleerd
- Dongle niet compatibel met Linux ARM
- USB poort defect

**Oplossingen**:

1. **Check dongle compatibiliteit**:
   ```bash
   # Vind USB ID
   lsusb
   # Zoek online of deze chipset Linux ondersteunt
   ```

2. **Installeer driver** (als nodig):
   ```bash
   # Voor Realtek dongles (veelvoorkomend)
   sudo apt update
   sudo apt install -y linux-firmware
   
   # Of compileer driver (afhankelijk van chipset)
   # Check dongle documentatie voor specifieke driver
   ```

3. **Check USB poort**:
   ```bash
   # Test of USB poort werkt
   lsusb  # Moet dongle tonen
   ```

## Stap 4: Configureer WiFi op Robot

### 4.1 Vind WiFi Interface Naam

```bash
# Vind nieuwe WiFi interface
ip link show | grep wlan

# Of:
iwconfig  # Toont alle WiFi interfaces

# Noteer de naam (bijvoorbeeld: wlan1, wlx1234567890ab)
```

### 4.2 Activeer WiFi Interface

```bash
# Activeer WiFi interface
sudo ip link set <interface-naam> up

# Bijvoorbeeld:
sudo ip link set wlan1 up

# Check status
ip link show <interface-naam>
# Moet "state UP" tonen
```

### 4.3 Scan voor WiFi Netwerken

```bash
# Scan voor beschikbare WiFi netwerken
sudo iwlist <interface-naam> scan | grep ESSID

# Of gebruik iw:
sudo iw dev <interface-naam> scan | grep SSID

# Bijvoorbeeld:
sudo iwlist wlan1 scan | grep ESSID
```

### 4.4 Verbind met WiFi Netwerk

#### Methode A: Via wpa_supplicant (Aanbevolen)

**Stap 1: Maak configuratiebestand**:
```bash
# Maak wpa_supplicant config
sudo nano /etc/wpa_supplicant/wpa_supplicant-<interface-naam>.conf
```

**Stap 2: Voeg WiFi netwerk toe**:
```conf
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1

network={
    ssid="JOUW_WIFI_NAAM"
    psk="JOUW_WIFI_WACHTWOORD"
    priority=1
}
```

**Stap 3: Start wpa_supplicant**:
```bash
# Stop eventuele bestaande wpa_supplicant
sudo killall wpa_supplicant

# Start wpa_supplicant voor nieuwe interface
sudo wpa_supplicant -B -i <interface-naam> -c /etc/wpa_supplicant/wpa_supplicant-<interface-naam>.conf

# Bijvoorbeeld:
sudo wpa_supplicant -B -i wlan1 -c /etc/wpa_supplicant/wpa_supplicant-wlan1.conf
```

**Stap 4: Vraag IP adres aan**:
```bash
# Via DHCP
sudo dhclient <interface-naam>

# Bijvoorbeeld:
sudo dhclient wlan1

# Check IP adres
ip addr show <interface-naam>
```

#### Methode B: Via NetworkManager (Als beschikbaar)

```bash
# Check of NetworkManager beschikbaar is
systemctl status NetworkManager

# Als beschikbaar:
sudo nmcli device wifi list  # Scan netwerken
sudo nmcli device wifi connect "JOUW_WIFI_NAAM" password "WACHTWOORD" ifname <interface-naam>
```

#### Methode C: Via netplan (Ubuntu/Debian)

```bash
# Maak netplan configuratie
sudo nano /etc/netplan/50-wifi-dongle.yaml
```

```yaml
network:
  version: 2
  renderer: networkd
  wifis:
    <interface-naam>:
      dhcp4: yes
      access-points:
        "JOUW_WIFI_NAAM":
          password: "JOUW_WIFI_WACHTWOORD"
```

```bash
# Pas configuratie toe
sudo netplan apply
```

### 4.5 Test WiFi Verbinding

```bash
# Check verbinding status
iwconfig <interface-naam>

# Check IP adres
ip addr show <interface-naam>

# Test internet verbinding
ping -c 4 8.8.8.8

# Test lokale netwerk verbinding
ping -c 4 <router-ip>  # Meestal 192.168.1.1 of 192.168.0.1
```

## Stap 5: Configureer Automatische Verbinding

### 5.1 Maak WiFi Verbinding Permanent

**Voor wpa_supplicant**:
```bash
# Maak systemd service
sudo nano /etc/systemd/system/wpa_supplicant-<interface-naam>.service
```

```ini
[Unit]
Description=WPA supplicant for USB WiFi dongle
After=network.target

[Service]
Type=forking
ExecStart=/usr/sbin/wpa_supplicant -B -i <interface-naam> -c /etc/wpa_supplicant/wpa_supplicant-<interface-naam>.conf
ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
```

```bash
# Activeer service
sudo systemctl enable wpa_supplicant-<interface-naam>.service
sudo systemctl start wpa_supplicant-<interface-naam>.service
```

**Voor netplan**:
- Configuratie wordt automatisch toegepast bij opstarten

### 5.2 Configureer DHCP Client

```bash
# Maak DHCP client service voor WiFi
sudo nano /etc/systemd/system/dhclient-<interface-naam>.service
```

```ini
[Unit]
Description=DHCP client for USB WiFi dongle
After=wpa_supplicant-<interface-naam>.service
Requires=wpa_supplicant-<interface-naam>.service

[Service]
Type=oneshot
ExecStart=/sbin/dhclient <interface-naam>
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

```bash
# Activeer service
sudo systemctl enable dhclient-<interface-naam>.service
sudo systemctl start dhclient-<interface-naam>.service
```

## Stap 6: Vind Robot IP Adres

### 6.1 Check IP Adres op Robot

```bash
# Check IP adres van WiFi interface
ip addr show <interface-naam>

# Of:
ifconfig <interface-naam>

# Noteer het IP adres (bijvoorbeeld: 192.168.1.100)
```

### 6.2 Vind IP Adres vanaf Computer

**Via netwerk scan**:
```bash
# Scan lokaal netwerk
nmap -sn 192.168.1.0/24

# Of gebruik arp
arp -a | grep -i "unitree\|go2"
```

**Via router**:
1. Log in op router (meestal `192.168.1.1`)
2. Ga naar **DHCP Clients** of **Connected Devices**
3. Zoek naar "Unitree" of "Go2"
4. Noteer IP adres

## Stap 7: Test Wireless Programmeren

### 7.1 Test Netwerk Verbinding

```bash
# Vanaf je computer, ping robot
ping <robot-ip>

# Bijvoorbeeld:
ping 192.168.1.100
```

### 7.2 Test SSH Verbinding

```bash
# Verbind met robot via SSH
ssh unitree@<robot-ip>
# Of:
ssh root@<robot-ip>
```

### 7.3 Test SDK Verbinding

```bash
# Test custom wrapper
python -c "
from src.unitree_go2 import Go2Robot
robot = Go2Robot(ip_address='<robot-ip>')
robot.connect()
print('✓ Verbinding succesvol!')
robot.disconnect()
"

# Test officiële SDK
python -c "
from src.unitree_go2 import Go2RobotOfficial
robot = Go2RobotOfficial(ip_address='<robot-ip>', network_interface='<jouw-wifi-interface>')
robot.connect()
print('✓ Verbinding succesvol!')
robot.disconnect()
"
```

## Compatibele WiFi Dongles

### Aanbevolen Dongles

| Model | Chipset | Linux Support | Opmerking |
|-------|----------|---------------|-----------|
| TP-Link TL-WN722N | Atheros AR9271 | ✅ Uitstekend | Goede Linux support |
| TP-Link TL-WN823N | Realtek RTL8192CU | ✅ Goed | Veel gebruikt |
| Edimax EW-7811Un | Realtek RTL8188CUS | ✅ Goed | Klein formaat |
| Panda PAU05 | Realtek RTL8192CU | ✅ Goed | USB 2.0 |
| Alfa AWUS036NH | Ralink RT3070 | ✅ Uitstekend | Hoge zendkracht |

### Check Compatibiliteit

**Voor aankoop**:
1. Check chipset (Realtek, Atheros, Ralink meestal goed)
2. Check Linux ARM support online
3. Vermijd dongles die alleen Windows/Mac ondersteunen

**Na aankoop**:
```bash
# Check USB ID
lsusb

# Zoek online: "USB ID <vendor>:<product> Linux support"
```

## Troubleshooting

### Probleem 1: Dongle Wordt Niet Herkend

**Oplossing**:
```bash
# Check USB verbinding
lsusb  # Moet dongle tonen

# Check dmesg voor errors
dmesg | tail -50

# Probeer dongle in andere USB poort
# Herstart robot
```

### Probleem 2: WiFi Interface Verschijnt Niet

**Oplossing**:
```bash
# Check of driver geladen is
lsmod | grep -i wifi

# Check dmesg voor driver errors
dmesg | grep -i "wifi\|80211\|rtl\|ath"

# Installeer firmware
sudo apt update
sudo apt install -y linux-firmware

# Herstart robot
```

### Probleem 3: Kan Niet Verbinden met WiFi

**Oplossing**:
```bash
# Check interface status
ip link show <interface-naam>  # Moet "state UP" zijn

# Check WiFi scan
sudo iwlist <interface-naam> scan

# Check wpa_supplicant logs
sudo journalctl -u wpa_supplicant-<interface-naam>.service -n 50

# Test handmatig
sudo wpa_supplicant -i <interface-naam> -c /etc/wpa_supplicant/wpa_supplicant-<interface-naam>.conf -d
```

### Probleem 4: Verbinding Val weg

**Oplossing**:
```bash
# Check signaalsterkte
iwconfig <interface-naam>  # Kijk naar "Signal level"

# Check power management
iwconfig <interface-naam> power off  # Zet power saving uit

# Check router instellingen
# - Zet AP isolation uit
# - Check MAC filtering
# - Check firewall regels
```

### Probleem 5: Kan Robot Niet Bereiken via WiFi

**Oplossing**:
```bash
# Check IP adres op robot
ip addr show <interface-naam>

# Check routing
ip route show

# Test vanaf computer
ping <robot-ip>

# Check firewall op robot
sudo iptables -L  # Check firewall regels

# Test SSH
ssh unitree@<robot-ip>
```

## Best Practices

### 1. Gebruik Korte USB Kabel

- Minder kans op losraken tijdens beweging
- Betere signaal kwaliteit
- Minder fysieke schade

### 2. Beveilig WiFi Dongle

- Gebruik WPA2 beveiliging
- Schakel ongebruikte WiFi netwerken uit
- Update firmware regelmatig

### 3. Monitor Verbinding

```bash
# Check verbinding status regelmatig
watch -n 5 'iwconfig <interface-naam>'

# Monitor logs
sudo journalctl -u wpa_supplicant-<interface-naam>.service -f
```

### 4. Backup Configuratie

```bash
# Backup WiFi configuratie
sudo cp /etc/wpa_supplicant/wpa_supplicant-<interface-naam>.conf ~/wifi-backup.conf

# Backup netplan config (als gebruikt)
sudo cp /etc/netplan/50-wifi-dongle.yaml ~/netplan-backup.yaml
```

## Alternatieve Methoden

### Als USB WiFi Dongle Niet Werkt

1. **Gebruik ingebouwde WiFi** (als beschikbaar):
   - Zie [WiFi Verbinding Guide](./WIFI_VERBINDING.md)

2. **Gebruik Ethernet**:
   - Zie [Ethernet Verbinding Guide](./ETHERNET_VERBINDING.md)

3. **Gebruik USB Tethering**:
   - Verbind telefoon via USB
   - Schakel USB tethering in

## Samenvatting

### Quick Start Checklist

- [ ] USB WiFi dongle aangesloten in Go2 USB poort
- [ ] Robot herkent dongle (`lsusb` toont dongle)
- [ ] WiFi interface gevonden (`ip link show`)
- [ ] WiFi interface geactiveerd (`ip link set <interface> up`)
- [ ] WiFi netwerk gescand (`iwlist <interface> scan`)
- [ ] Verbonden met WiFi netwerk (wpa_supplicant of NetworkManager)
- [ ] IP adres verkregen (`ip addr show <interface>`)
- [ ] Verbinding getest (`ping <robot-ip>`)
- [ ] SSH toegang werkt (`ssh unitree@<robot-ip>`)
- [ ] SDK verbinding werkt (test script)
- [ ] Automatische verbinding geconfigureerd (systemd service)

### Belangrijkste Commando's

```bash
# Check USB devices
lsusb

# Check netwerk interfaces
ip link show

# Activeer WiFi interface
sudo ip link set wlan1 up

# Scan WiFi netwerken
sudo iwlist wlan1 scan

# Verbind met WiFi (via wpa_supplicant)
sudo wpa_supplicant -B -i wlan1 -c /etc/wpa_supplicant/wpa_supplicant-wlan1.conf
sudo dhclient wlan1

# Check IP adres
ip addr show wlan1

# Test verbinding
ping <robot-ip>
```

## Referenties

- [WiFi Verbinding Guide](./WIFI_VERBINDING.md) - Ingebouwde WiFi configuratie
- [Ethernet Verbinding Guide](./ETHERNET_VERBINDING.md) - Ethernet alternatief
- [SSH Toegang](./VOICE_OP_ROBOT.md) - SSH configuratie op robot
- [Unitree Go2 Handleiding](./GO2_HANDLEIDING.md) - Algemene robot handleiding

## Contact Ondersteuning

Als je problemen hebt:

1. **Check dongle compatibiliteit**: Zoek online naar Linux ARM support
2. **Check Unitree Forums**: Community forums voor Go2
3. **Unitree Support**: https://support.unitree.com
4. **Linux WiFi Communities**: Voor driver problemen

