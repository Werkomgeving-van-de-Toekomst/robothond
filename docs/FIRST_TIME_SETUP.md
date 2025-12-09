# First Time Setup Guide voor Go2 Robot

Complete guide voor eerste keer gebruik van de Go2 robot.

## Overzicht

Dit guide helpt je bij het opzetten van je Go2 robot voor de eerste keer. We testen alles stap voor stap om te zorgen dat alles werkt.

## Snel Starten

### Stap 1: Run Setup Test

```bash
python src/examples/first_time_setup_test.py
```

Dit script test:
- ✅ Alle imports werken
- ✅ CycloneDDS geïnstalleerd
- ✅ Netwerk verbinding met robot
- ✅ Custom wrapper werkt
- ✅ Officiële SDK werkt

### Stap 2: Volg Aanbevelingen

Het script geeft aanbevelingen voor eventuele problemen.

## Gedetailleerde Setup

### ⚠️ Belangrijk: Python Versie

**CycloneDDS werkt niet met Python 3.14!** Gebruik Python 3.12 of 3.11.

```bash
# Check Python versie
python --version

# Als je Python 3.14 hebt, maak nieuwe venv met Python 3.12:
python3.12 -m venv venv
source venv/bin/activate

# Of gebruik het setup script:
./setup_venv_python312.sh
```

### 1. Installeer Dependencies

```bash
# Activeer virtual environment
source venv/bin/activate  # Of conda activate pybullet

# Installeer basis dependencies
pip install -r requirements.txt
```

### 2. Installeer CycloneDDS (voor officiële SDK)

```bash
# Automatisch (aanbevolen)
./install_cyclonedds_macos.sh

# Of handmatig (zie docs/OFFICIELE_SDK_INTEGRATIE.md)
```

### 3. Test Setup

```bash
# Volledige test
python src/examples/first_time_setup_test.py

# Zonder robot tests (alleen configuratie)
python src/examples/first_time_setup_test.py --skip-robot

# Met custom IP
python src/examples/first_time_setup_test.py -i 192.168.123.161

# Met netwerk interface voor officiële SDK
python src/examples/first_time_setup_test.py --interface en0
```

## Test Script Opties

### Basis Gebruik

```bash
python src/examples/first_time_setup_test.py
```

### Met Opties

```bash
# Custom IP adres
python src/examples/first_time_setup_test.py -i 192.168.1.100

# Specifieke netwerk interface
python src/examples/first_time_setup_test.py --interface en0

# Skip robot tests (alleen configuratie check)
python src/examples/first_time_setup_test.py --skip-robot
```

## Wat het Script Test

### 1. Imports Test

- Custom wrapper (`Go2Robot`)
- Officiële SDK (`Go2RobotOfficial`)
- Extra modules (FlowExecutor, WebSearcher)

### 2. CycloneDDS Test

- `CYCLONEDDS_HOME` environment variable
- CycloneDDS directory bestaat
- cyclonedds Python package geïnstalleerd

### 3. Netwerk Test

- Socket verbinding naar robot
- Ping test naar robot IP

### 4. Custom Wrapper Test

- Verbinding maken
- Stand commando
- Stop commando

### 5. Officiële SDK Test

- Verbinding via DDS
- Stand commando
- Stop commando

## Troubleshooting

### "Imports mislukt"

```bash
# Installeer dependencies
pip install -r requirements.txt

# Check Python versie (vereist 3.8+)
python --version
```

### "CYCLONEDDS_HOME niet gezet"

```bash
# Export voor deze sessie
export CYCLONEDDS_HOME="/Users/marc/cyclonedds/install"

# Of gebruik install script
./install_cyclonedds_macos.sh
```

### "Netwerk verbinding mislukt"

1. **Check robot status**:
   - Is robot aan?
   - Zie je LED indicatoren?

2. **Check netwerk verbinding**:
   - Is robot verbonden met WiFi?
   - Zie [WiFi Verbinding Guide](./WIFI_VERBINDING.md) voor WiFi instructies
   - Of gebruik Ethernet: Zie [Ethernet Verbinding Guide](./ETHERNET_VERBINDING.md) voor directe verbinding

3. **Check IP adres**:
   ```bash
   ping 192.168.123.161
   ```

4. **Check netwerk**:
   - Zit je op hetzelfde netwerk?
   - Check WiFi/Ethernet verbinding

5. **Check firewall**:
   - Staat poort 8080 open?
   - Test met: `telnet 192.168.123.161 8080`
   - Zie [Firewall Troubleshooting](./FIREWALL_TROUBLESHOOTING.md) voor gedetailleerde instructies

### "Robot commando's werken niet"

1. **Check EDU variant**:
   ```bash
   python src/examples/test_edu_variant.py
   ```

2. **Check ontwikkelaarsmodus**:
   - Open Unitree Go app
   - Ga naar Settings
   - Check "Developer Mode"

3. **Check robot firmware**:
   - Update via Unitree Go app indien nodig

### "Officiële SDK werkt niet"

1. **Check CycloneDDS**:
   ```bash
   echo $CYCLONEDDS_HOME
   # Moet pad tonen naar cyclonedds/install
   ```

2. **Check netwerk interface**:
   ```bash
   # macOS
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Gebruik interface naam in test
   python src/examples/first_time_setup_test.py --interface en0
   ```

3. **Check DDS communicatie**:
   - Zorg dat robot op hetzelfde netwerk zit
   - Check firewall voor DDS poorten

## Eerste Commando's

Na succesvolle setup test:

### Custom Wrapper

```python
from src.unitree_go2 import Go2Robot

with Go2Robot(ip_address="192.168.123.161") as robot:
    robot.stand()
    robot.move(vx=0.3, vy=0.0, vyaw=0.0)
    time.sleep(2.0)
    robot.stop()
    robot.sit()
```

### Officiële SDK

```python
from src.unitree_go2 import Go2RobotOfficial

with Go2RobotOfficial(
    ip_address="192.168.123.161",
    network_interface="en0"
) as robot:
    robot.stand()
    robot.move(vx=0.3, vy=0.0, vyaw=0.0)
    time.sleep(2.0)
    robot.stop()
```

## Checklist

Gebruik deze checklist voor eerste keer setup:

- [ ] Dependencies geïnstalleerd (`pip install -r requirements.txt`)
- [ ] CycloneDDS gecompileerd (als je officiële SDK wilt gebruiken)
- [ ] `CYCLONEDDS_HOME` gezet (als je officiële SDK wilt gebruiken)
- [ ] Robot aan en verbonden met netwerk
- [ ] IP adres bekend (standaard: 192.168.123.161)
- [ ] Setup test script gerund
- [ ] Alle tests geslaagd
- [ ] Eerste commando's getest

## Volgende Stappen

Na succesvolle setup:

1. **Bekijk voorbeelden**: `src/examples/`
2. **Lees handleiding**: `docs/GO2_HANDLEIDING.md`
3. **Probeer flows**: `python src/examples/run_flow.py --flow welcome`
4. **Test voice control**: `python src/examples/voice_control.py`
5. **Experimenteer**: Maak je eigen scripts!

## Referenties

- [Go2 Handleiding](./GO2_HANDLEIDING.md)
- [Go2 SDK Referentie](./GO2_SDK_REFERENTIE.md)
- [Officiële SDK Integratie](./OFFICIELE_SDK_INTEGRATIE.md)
- [EDU Variant Identificatie](./GO2_EDU_IDENTIFICATIE.md)

