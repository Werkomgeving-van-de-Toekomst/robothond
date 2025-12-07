# Quick Start Guide - Unitree Go2 EDU

## Stap 1: Eerste Setup (eenmalig)

### 1.1 Virtual environment aanmaken en dependencies installeren

```bash
# Maak virtual environment aan
python3 -m venv venv

# Activeer virtual environment
source venv/bin/activate  # Op macOS/Linux
# of: venv\Scripts\activate  # Op Windows

# Installeer dependencies
pip install -r requirements.txt
```

**Let op**: Vergeet niet de virtual environment te activeren voordat je scripts uitvoert!

### 1.2 Robot configureren

Pas indien nodig het IP adres aan in `config/robot_config.yaml`:
```yaml
robot:
  ip_address: "192.168.123.161"  # Pas aan naar jouw robot IP
```

## Stap 2: Robot Verbinden

### 2.1 Zorg dat robot aan staat en verbonden is

- Zet de robot aan
- Zorg dat robot en computer op hetzelfde netwerk zitten
- Controleer het IP adres van de robot (meestal 192.168.123.161)

### 2.2 Voer diagnostiek uit

```bash
python src/examples/diagnostics.py
```

Of met custom IP:
```bash
python src/examples/diagnostics.py -i 192.168.123.161
```

Dit script controleert:
- ✓ Netwerkverbinding
- ✓ SDK verbinding
- ✓ Basis commando's (stand, sit, stop)
- ✓ Sensor data lezen
- ✓ Beweging functionaliteit

## Stap 3: Tests Uitvoeren

### 3.1 Automatisch testen (aanbevolen)

Het automatische test script wacht tot de robot verbonden is en voert dan automatisch alle tests uit:

```bash
# Wacht op robot en voer alle tests uit
python auto_test.py

# Met custom IP adres
python auto_test.py -i 192.168.123.161

# Continue modus (herhaalt tests elke 60 seconden)
python auto_test.py --continuous

# Alleen specifieke test categorieën
python auto_test.py -c connection -c commands
```

### 3.2 Handmatig tests uitvoeren

```bash
python run_tests.py
```

### 3.2 Specifieke test categorieën

```bash
# Alleen verbinding tests
python run_tests.py -c connection

# Verbinding en commando tests
python run_tests.py -c connection -c commands

# Alle tests met verbose output
python run_tests.py -v
```

### 3.3 Test categorieën

- **connection**: Test verbindingsfunctionaliteit
- **commands**: Test basis commando's (stand, sit, move, stop)
- **sensors**: Test sensor data lezen
- **errors**: Test error handling
- **performance**: Test performance en latency

## Stap 4: Voorbeelden Uitproberen

### 4.1 Basis beweging

```bash
python src/examples/basic_movement.py
```

### 4.2 Sensor data lezen

```bash
python src/examples/read_sensors.py
```

## Troubleshooting

### Robot niet bereikbaar

1. Controleer of robot aan staat
2. Controleer IP adres: `ping 192.168.123.161`
3. Controleer of beide apparaten op hetzelfde netwerk zitten
4. Controleer firewall instellingen

### SDK commando's werken niet

1. Controleer of robot in ontwikkelaarsmodus staat
2. Controleer of de SDK correct is geïnstalleerd
3. Bekijk de officiële documentatie: https://support.unitree.com/home/en/developer

### Tests falen

1. Voer eerst diagnostiek uit: `python src/examples/diagnostics.py`
2. Controleer de error messages in de test output
3. Zorg dat robot niet in gebruik is door andere applicaties

## Volgende Stappen

Na het succesvol uitvoeren van de tests kun je:

1. Je eigen code schrijven met de `Go2Robot` klasse
2. De voorbeelden aanpassen voor jouw use case
3. Nieuwe functionaliteit toevoegen aan de SDK wrapper

## Hulp Nodig?

- Bekijk `docs/API.md` voor API documentatie
- Bekijk `README.md` voor algemene informatie
- Raadpleeg de officiële Unitree documentatie: https://support.unitree.com/home/en/developer

