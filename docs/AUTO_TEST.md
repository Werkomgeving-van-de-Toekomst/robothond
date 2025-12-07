# Automatisch Test Script Documentatie

Het `auto_test.py` script wacht automatisch tot de robot verbonden is en voert dan alle tests uit.

## Basis Gebruik

### Eenvoudigste vorm

```bash
python auto_test.py
```

Dit script:
1. Wacht tot de robot bereikbaar is op het standaard IP adres (192.168.123.161)
2. Test de verbinding
3. Voert alle tests uit
4. Toont een samenvatting

### Met custom IP adres

```bash
python auto_test.py -i 192.168.123.161
```

## Geavanceerde Opties

### Specifieke test categorieën

Voer alleen bepaalde test categorieën uit:

```bash
# Alleen verbinding tests
python auto_test.py -c connection

# Verbinding en commando tests
python auto_test.py -c connection -c commands

# Alle categorieën behalve performance
python auto_test.py -c connection -c commands -c sensors -c errors
```

### Continue modus

Herhaal tests automatisch:

```bash
# Tests elke 60 seconden (standaard)
python auto_test.py --continuous

# Tests elke 30 seconden
python auto_test.py --continuous --interval 30
```

Dit is handig voor:
- Langdurige monitoring
- Detecteren van verbindingsproblemen
- Performance monitoring over tijd

### Wachttijd instellingen

```bash
# Check elke 5 seconden in plaats van 2
python auto_test.py --check-interval 5

# Maximale wachttijd van 5 minuten
python auto_test.py --max-wait 300

# Wacht niet, voer direct tests uit (robot moet al verbonden zijn)
python auto_test.py --no-wait
```

### Verbose output

Voor gedetailleerde test output:

```bash
python auto_test.py -v
```

## Voorbeelden

### Scenario 1: Eerste keer opzetten

```bash
# Start script, zet robot aan, script detecteert automatisch
python auto_test.py
```

### Scenario 2: Monitoring tijdens ontwikkeling

```bash
# Voer tests continu uit om te zien of alles blijft werken
python auto_test.py --continuous --interval 30 -v
```

### Scenario 3: Snelle verbinding test

```bash
# Alleen verbinding tests, geen wachttijd
python auto_test.py --no-wait -c connection
```

### Scenario 4: Custom configuratie

```bash
# Custom IP, alleen commando tests, verbose, continue modus
python auto_test.py -i 192.168.1.100 -c commands -v --continuous --interval 120
```

## Output

Het script geeft duidelijke feedback:

```
======================================================================
  Unitree Go2 EDU Automatisch Test Script
======================================================================

Robot IP: 192.168.123.161
Starttijd: 2024-01-15 10:30:00

🔍 Wachten op robot op 192.168.123.161...
   (Druk Ctrl+C om te annuleren)

✓ Robot gevonden na 4.2 seconden (3 pogingen)

🔌 Testen verbinding...
✓ Verbinding OK

======================================================================
  Tests Uitvoeren
======================================================================

📋 Test categorie: CONNECTION
----------------------------------------------------------------------
✓ GESLAAGD - connection (2.34s)

[... meer tests ...]

======================================================================
  Test Samenvatting
======================================================================

Categorie            Status          Tijd      
----------------------------------------------------------------------
connection            ✓ GESLAAGD      2.34s
commands              ✓ GESLAAGD      15.67s
sensors               ✓ GESLAAGD      3.45s
errors                ✓ GESLAAGD      1.23s
performance           ✓ GESLAAGD      8.90s
----------------------------------------------------------------------
TOTAAL                                  31.59s

======================================================================
  ✓ ALLE TESTS GESLAAGD!
======================================================================
```

## Troubleshooting

### Robot wordt niet gedetecteerd

- Controleer of robot aan staat
- Controleer IP adres: `ping 192.168.123.161`
- Controleer netwerkverbinding
- Verhoog `--check-interval` als robot langzaam opstart

### Tests falen direct

- Gebruik `--no-wait` om te zien of het een verbindingsprobleem is
- Voer eerst `python src/examples/diagnostics.py` uit
- Controleer of robot in ontwikkelaarsmodus staat

### Continue modus stopt plotseling

- Controleer of robot nog verbonden is
- Script wacht automatisch tot robot weer bereikbaar is
- Druk Ctrl+C om handmatig te stoppen

## Integratie met andere tools

Het script kan geïntegreerd worden in:
- CI/CD pipelines (met `--no-wait`)
- Monitoring systemen (met `--continuous`)
- Development workflows
- Automated testing suites

