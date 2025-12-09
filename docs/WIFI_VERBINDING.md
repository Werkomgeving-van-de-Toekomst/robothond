# WiFi Verbinding Guide voor Go2 Robot

Complete guide voor het verbinden van de Go2 robot met je WiFi netwerk.

## Overzicht

De Go2 robot kan op twee manieren met WiFi verbinden:
1. **Access Point Modus**: Robot maakt eigen WiFi netwerk (standaard)
2. **Client Modus**: Robot verbindt met bestaand WiFi netwerk (aanbevolen)

## Methode 1: Via Unitree Go App (Aanbevolen)

### Stap 1: Download App

- **iOS**: [Unitree Go App](https://apps.apple.com/us/app/unitree-go-embodied-ai/id1579283821)
- **Android**: Zoek "Unitree Go" in Google Play Store

### Stap 2: Verbind met Robot Access Point

1. **Zet robot aan**
2. **Wacht tot robot opstart** (ongeveer 30 seconden)
3. **Open WiFi instellingen** op je telefoon
4. **Zoek naar robot WiFi netwerk**:
   - Naam begint meestal met "Unitree-Go2-" of "Go2-"
   - Bijvoorbeeld: `Unitree-Go2-XXXX` of `Go2-XXXX`
5. **Verbind met robot WiFi** (geen wachtwoord nodig voor eerste verbinding)

### Stap 3: Configureer WiFi via App

1. **Open Unitree Go app**
2. **App detecteert robot automatisch** (als je verbonden bent met robot WiFi)
3. **Ga naar Settings** (Instellingen)
4. **Zoek naar "WiFi Settings"** of "Netwerk Instellingen"
5. **Selecteer je WiFi netwerk** uit de lijst
6. **Voer WiFi wachtwoord in**
7. **Bevestig verbinding**

### Stap 4: Wacht op Verbinding

- Robot verbreekt Access Point modus
- Robot verbindt met je WiFi netwerk
- Dit kan 30-60 seconden duren
- LED indicatoren tonen verbindingsstatus

### Stap 5: Vind Robot IP Adres

**Via App**:
- Ga naar **Robot Info** of **Settings**
- Zoek naar **IP Address** of **Network Info**
- Noteer het IP adres (bijvoorbeeld: `192.168.1.100`)

**Via Netwerk Scanner** (als app geen IP toont):
```bash
# Scan lokaal netwerk voor robot
# macOS/Linux
nmap -sn 192.168.1.0/24 | grep -B 2 "Unitree\|Go2"

# Of gebruik arp
arp -a | grep -i "unitree\|go2"
```

## Methode 2: Via Robot Access Point en Browser

### Stap 1: Verbind met Robot WiFi

1. **Zet robot aan**
2. **Verbind met robot WiFi** op je computer/telefoon
3. **Naam**: `Unitree-Go2-XXXX` of `Go2-XXXX`
4. **Wachtwoord**: Meestal geen, of `12345678` (check handleiding)

### Stap 2: Open Web Interface

1. **Open browser** (Chrome, Safari, Firefox)
2. **Ga naar**: `http://192.168.123.1` of `http://192.168.123.161`
3. **Of probeer**: `http://unitree.local` of `http://go2.local`

### Stap 3: Configureer WiFi

1. **Login** (indien nodig):
   - Gebruikersnaam: `admin` of `unitree`
   - Wachtwoord: `admin` of `12345678` (check handleiding)
2. **Ga naar WiFi Settings**
3. **Selecteer je WiFi netwerk**
4. **Voer wachtwoord in**
5. **Klik op "Connect"** of "Save"

### Stap 4: Wacht en Test

- Wacht 30-60 seconden
- Robot verbindt met je WiFi
- Test verbinding: `ping <robot-ip>`

## Methode 3: Via Robot Interface (Fysieke Knoppen)

Sommige Go2 modellen hebben een fysieke WiFi configuratie modus:

1. **Zet robot uit**
2. **Houd aan/uit knop ingedrukt** (5-10 seconden)
3. **LED indicatoren tonen WiFi configuratie modus**
4. **Volg instructies in handleiding** voor specifieke modellen

## Troubleshooting: Robot Verbindt Niet met WiFi

### Probleem 1: Robot WiFi Netwerk Verschijnt Niet

**Mogelijke oorzaken**:
- Robot is niet volledig opgestart
- WiFi module is defect
- Robot is al verbonden met ander netwerk

**Oplossingen**:
1. **Wacht langer** (tot 60 seconden na opstarten)
2. **Herstart robot**:
   - Zet uit
   - Wacht 10 seconden
   - Zet weer aan
3. **Reset WiFi** (zie reset sectie hieronder)
4. **Check LED indicatoren**:
   - Blauw knipperend = WiFi actief
   - Rood = Fout
   - Groen = Verbonden

### Probleem 2: Kan Niet Verbinden met Robot WiFi

**Mogelijke oorzaken**:
- Verkeerd WiFi netwerk geselecteerd
- WiFi wachtwoord vereist
- Te ver van robot

**Oplossingen**:
1. **Check WiFi naam**: Moet beginnen met "Unitree-" of "Go2-"
2. **Probeer wachtwoord**: `12345678` of leeg
3. **Kom dichterbij**: Binnen 5 meter van robot
4. **Herstart robot WiFi**:
   - Zet robot uit en aan
   - Of gebruik reset knop (zie handleiding)

### Probleem 3: Robot Verbindt Niet met Mijn WiFi

**Mogelijke oorzaken**:
- Verkeerd WiFi wachtwoord
- WiFi netwerk niet ondersteund (5GHz alleen, WPA3, etc.)
- Router blokkeert robot
- Robot te ver van router

**Oplossingen**:

#### 1. Check WiFi Wachtwoord
- Zorg dat wachtwoord correct is (hoofdletters/kleine letters)
- Probeer wachtwoord opnieuw in te voeren
- Check voor speciale tekens

#### 2. Check WiFi Netwerk Type
**Go2 ondersteunt meestal**:
- ✅ 2.4 GHz WiFi (aanbevolen)
- ✅ WPA2 beveiliging
- ✅ WPA/WPA2 mixed mode

**Mogelijk niet ondersteund**:
- ❌ 5 GHz alleen netwerken
- ❌ WPA3 alleen
- ❌ Enterprise WiFi (WPA2-Enterprise)
- ❌ Hidden SSID netwerken

**Oplossing**:
- Gebruik 2.4 GHz netwerk (of dual-band met 2.4 GHz)
- Schakel WPA3 uit, gebruik WPA2
- Maak WiFi netwerk zichtbaar (niet hidden)

#### 3. Check Router Instellingen

**MAC Address Filtering**:
```bash
# Vind robot MAC address (via app of web interface)
# Voeg toe aan router whitelist
```

**AP Isolation / Client Isolation**:
- Schakel uit in router instellingen
- Dit voorkomt dat apparaten elkaar zien

**Firewall Regels**:
- Sta robot toe om verbinding te maken
- Check router firewall logs

#### 4. Check Afstand en Signaal

- **Minimum afstand**: Binnen 10 meter van router
- **Check signaalsterkte**: Minimaal 50% in app
- **Vermijd obstakels**: Muren, metalen objecten

#### 5. Reset Robot WiFi

**Soft Reset**:
1. Via app: Settings → Reset WiFi
2. Of: Zet robot uit en aan

**Hard Reset** (laatste redmiddel):
1. Zet robot uit
2. Houd reset knop ingedrukt (check handleiding voor locatie)
3. Zet robot aan terwijl reset knop ingedrukt
4. Houd 10 seconden vast
5. Laat los
6. Robot reset naar fabrieksinstellingen

### Probleem 4: Robot Verbindt maar Verliest Verbinding

**Mogelijke oorzaken**:
- Zwak WiFi signaal
- Router herstart
- IP conflict
- Power saving modus

**Oplossingen**:
1. **Check signaalsterkte**: Minimaal 50%
2. **Vermijd power saving**: Zet uit in router instellingen
3. **Static IP toewijzen**: Via router DHCP reservations
4. **Update firmware**: Check voor updates via app

### Probleem 5: Kan Robot IP Niet Vinden

**Oplossingen**:

**Via App**:
- Ga naar Robot Info → Network Info
- Of Settings → IP Address

**Via Netwerk Scan**:
```bash
# macOS/Linux - Scan lokaal netwerk
nmap -sn 192.168.1.0/24

# Of gebruik arp table
arp -a

# Check router DHCP client list
# Log in op router (meestal 192.168.1.1 of 192.168.0.1)
# Ga naar DHCP Clients of Connected Devices
```

**Via Router**:
1. Log in op router (meestal `192.168.1.1` of `192.168.0.1`)
2. Ga naar **DHCP Clients** of **Connected Devices**
3. Zoek naar "Unitree" of "Go2"
4. Noteer IP adres

## WiFi Netwerk Vereisten

### Aanbevolen Instellingen

- **Frequentie**: 2.4 GHz (aanbevolen) of dual-band
- **Beveiliging**: WPA2
- **Kanaal**: Auto of 1, 6, 11 (voor 2.4 GHz)
- **SSID**: Zichtbaar (niet hidden)
- **MAC Filtering**: Uit
- **AP Isolation**: Uit
- **Power Saving**: Uit

### Niet Ondersteund

- ❌ 5 GHz alleen netwerken
- ❌ WPA3 alleen beveiliging
- ❌ Enterprise WiFi (WPA2-Enterprise)
- ❌ Hidden SSID
- ❌ MAC filtering (tenzij robot toegevoegd)
- ❌ VPN netwerken

## Alternatieve Verbindingsmethoden

### Ethernet (als beschikbaar)

Sommige Go2 modellen hebben Ethernet poort:

1. **Sluit Ethernet kabel aan** op robot
2. **Sluit andere kant aan** op router/switch
3. **Robot krijgt automatisch IP** via DHCP
4. **Vind IP via router** of netwerk scan

### USB Tethering (Android)

1. **Verbind telefoon met robot** via USB
2. **Schakel USB tethering in** op telefoon
3. **Robot gebruikt telefoon internet**
4. **IP adres**: Meestal `192.168.42.x`

## Testen van Verbinding

### Stap 1: Test Netwerk Verbinding

```bash
# Ping robot IP
ping 192.168.123.161

# Of gebruik diagnostiek script
python src/examples/diagnostics.py -i 192.168.123.161
```

### Stap 2: Test SDK Verbinding

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

### Stap 3: Test Officiële SDK

```bash
# Test officiële SDK (als geïnstalleerd)
python -c "
from src.unitree_go2 import Go2RobotOfficial
robot = Go2RobotOfficial(ip_address='192.168.123.161', network_interface='en0')
robot.connect()
print('✓ Verbinding succesvol!')
robot.disconnect()
"
```

## Veelgestelde Vragen (FAQ)

### Q: Moet ik altijd via robot WiFi verbinden?

**A**: Nee, alleen voor eerste configuratie. Daarna verbindt robot direct met je WiFi.

### Q: Kan ik robot gebruiken zonder internet?

**A**: Ja, robot werkt op lokaal netwerk. Internet is alleen nodig voor:
- Firmware updates
- App cloud features
- Remote access (indien geconfigureerd)

### Q: Hoeveel robots kunnen op één WiFi netwerk?

**A**: Meestal onbeperkt, maar check router limieten. Elke robot heeft eigen IP.

### Q: Kan ik robot IP adres wijzigen?

**A**: Meestal via router DHCP reservations, of static IP via app/web interface.

### Q: Werkt robot met mesh WiFi netwerken?

**A**: Meestal wel, maar kan problemen geven. Gebruik hoofdrouter indien mogelijk.

### Q: Kan ik robot gebruiken op publiek WiFi?

**A**: Meestal niet, omdat:
- Publiek WiFi heeft vaak AP isolation
- Wachtwoord vereist browser login
- Beperkte netwerk toegang

## Reset WiFi Instellingen

### Soft Reset (via App)

1. Open Unitree Go app
2. Ga naar Settings → WiFi Settings
3. Klik op "Reset WiFi" of "Forget Network"
4. Robot keert terug naar Access Point modus

### Hard Reset (Fysiek)

1. **Zet robot uit**
2. **Houd reset knop ingedrukt** (check handleiding voor locatie)
3. **Zet robot aan** terwijl reset knop ingedrukt
4. **Houd 10 seconden vast**
5. **Laat los**
6. Robot reset naar fabrieksinstellingen

**Let op**: Hard reset verwijdert alle instellingen!

## Contact Ondersteuning

Als niets werkt:

1. **Check handleiding**: Specifieke instructies voor jouw model
2. **Unitree Support**: https://support.unitree.com
3. **Community Forums**: Unitree community forums
4. **Email Support**: Check Unitree website voor contact

## Referenties

- [Go2 Handleiding](./GO2_HANDLEIDING.md)
- [First Time Setup](./FIRST_TIME_SETUP.md)
- [Firewall Troubleshooting](./FIREWALL_TROUBLESHOOTING.md)
- [Unitree Go App](https://apps.apple.com/us/app/unitree-go-embodied-ai/id1579283821)

## Samenvatting

**Snelste Methode**:
1. Download Unitree Go app
2. Verbind met robot WiFi (`Unitree-Go2-XXXX`)
3. Configureer WiFi via app
4. Wacht op verbinding
5. Vind IP adres in app
6. Test verbinding

**Als het niet werkt**:
- Check WiFi netwerk type (2.4 GHz, WPA2)
- Reset robot WiFi
- Check router instellingen
- Probeer dichter bij router te staan

