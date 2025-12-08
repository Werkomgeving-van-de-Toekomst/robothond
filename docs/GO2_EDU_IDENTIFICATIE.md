# Unitree Go2 EDU Variant Identificatie

Hoe te bepalen of je de EDU (Educational) variant van de Unitree Go2 hebt.

## Belangrijk Verschil

De **EDU variant** heeft ontwikkelaarsmodus en SDK toegang, terwijl de **standaard variant** beperkte functionaliteit heeft.

## Identificatie Methoden

### Methode 1: Check via Unitree Go App

1. **Open Unitree Go app** op je telefoon
2. **Ga naar Settings** (Instellingen)
3. **Zoek naar "Developer Mode"** of "Ontwikkelaarsmodus"
4. **Check robot informatie**:
   - EDU variant: Toont "EDU" of "Educational" in model informatie
   - Standaard variant: Geen EDU vermelding

### Methode 2: Check via Robot Interface

1. **Zet robot aan**
2. **Druk lang op de aan/uit knop** (meestal 3-5 seconden)
3. **Check LED indicatoren**:
   - EDU variant: Mogelijk speciale LED patronen voor ontwikkelaarsmodus
   - Check handleiding voor specifieke patronen

### Methode 3: Check via SDK Verbinding

Probeer verbinding te maken met de SDK:

```bash
# Test verbinding
python src/examples/diagnostics.py -i 192.168.123.161
```

**Resultaten**:
- **EDU variant**: Verbinding succesvol, commando's werken
- **Standaard variant**: Geen verbinding of commando's worden genegeerd

### Methode 4: Check via Web Interface

1. **Verbind met robot WiFi** (als beschikbaar)
2. **Open browser**: Ga naar `http://192.168.123.161` of robot IP
3. **Check interface**:
   - EDU variant: Toont ontwikkelaarsopties, SDK status
   - Standaard variant: Beperkte interface

### Methode 5: Check Aankoop Documenten

**EDU variant kenmerken**:
- Product naam bevat "EDU" of "Educational"
- Inclusief SDK licentie/activatie code
- Specifieke EDU verpakking/documentatie
- Hogere prijs dan standaard variant

### Methode 6: Check Firmware Versie

Via de Unitree Go app:

1. **Ga naar Robot Info**
2. **Check Firmware Versie**
3. **EDU variant**: Mogelijk specifieke firmware versie met "EDU" in naam

## Functies die EDU Variant Heeft

Als je deze functies kunt gebruiken, heb je waarschijnlijk de EDU variant:

### ✅ SDK Toegang

```python
from src.unitree_go2 import Go2Robot

robot = Go2Robot(ip_address="192.168.123.161")
robot.connect()  # Werkt alleen met EDU variant
```

### ✅ Custom Commando's

```python
robot.move(vx=0.3, vy=0.0, vyaw=0.0)  # Werkt alleen met EDU
robot.stand()  # Werkt alleen met EDU
robot.sit()  # Werkt alleen met EDU
```

### ✅ Sensor Data Toegang

```python
state = robot.get_state()  # Werkt alleen met EDU
```

### ✅ Developer Mode

- Toegang tot ontwikkelaarsinstellingen
- SDK API endpoints beschikbaar
- Custom programming mogelijk

## Functies die Standaard Variant Heeft

De standaard variant heeft meestal:
- ✅ Basis beweging via app
- ✅ Voice commando's
- ✅ Camera functionaliteit
- ❌ Geen SDK toegang
- ❌ Geen custom programming
- ❌ Geen ontwikkelaarsmodus

## Test Script

Gebruik dit script om te testen of je EDU variant hebt:

```python
#!/usr/bin/env python3
"""
Test of je Go2 EDU variant hebt
"""

from src.unitree_go2 import Go2Robot, Go2ConnectionError

def test_edu_variant(ip_address="192.168.123.161"):
    """Test of robot EDU variant is"""
    
    print("=" * 70)
    print("  Go2 EDU Variant Test")
    print("=" * 70)
    print(f"\nTest verbinding met robot op {ip_address}...")
    
    try:
        robot = Go2Robot(ip_address=ip_address)
        robot.connect()
        print("✓ Verbinding succesvol!")
        
        # Test basis commando
        print("\nTest basis commando (stand)...")
        try:
            result = robot.stand()
            print("✓ Stand commando werkt!")
            print(f"  Resultaat: {result}")
            
            # Test sensor data
            print("\nTest sensor data ophalen...")
            state = robot.get_state()
            print("✓ Sensor data toegankelijk!")
            print(f"  Batterij: {state.get('battery_level', 'N/A')}%")
            
            print("\n" + "=" * 70)
            print("  ✅ JE HEBT WAARSCHIJNLIJK DE EDU VARIANT!")
            print("=" * 70)
            print("\nAlle SDK functies werken correct.")
            
            robot.disconnect()
            return True
            
        except Exception as e:
            print(f"⚠️  Commando test mislukt: {e}")
            print("\nDit kan betekenen:")
            print("  - Je hebt de standaard variant (geen SDK toegang)")
            print("  - Ontwikkelaarsmodus is niet ingeschakeld")
            print("  - Robot firmware is niet up-to-date")
            robot.disconnect()
            return False
            
    except Go2ConnectionError as e:
        print(f"❌ Verbindingsfout: {e}")
        print("\nMogelijke oorzaken:")
        print("  - Robot is niet aan")
        print("  - Verkeerd IP adres")
        print("  - Netwerkproblemen")
        print("  - Firewall blokkeert verbinding")
        return False
    except Exception as e:
        print(f"❌ Onverwachte fout: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.123.161"
    test_edu_variant(ip)
```

**Gebruik**:
```bash
python src/examples/test_edu_variant.py 192.168.123.161
```

## Als je Standaard Variant Hebt

Als je de standaard variant hebt, zijn er beperkte opties:

1. **Contact Unitree**: Vraag naar upgrade naar EDU variant
2. **Gebruik App Functionaliteit**: Gebruik de Unitree Go app voor basis controle
3. **Check Firmware Updates**: Soms worden EDU features toegevoegd in updates

## Als je EDU Variant Hebt maar SDK Werkt Niet

1. **Check Ontwikkelaarsmodus**: Zorg dat ontwikkelaarsmodus is ingeschakeld
2. **Update Firmware**: Zorg dat robot firmware up-to-date is
3. **Check Netwerk**: Zorg dat je op hetzelfde netwerk zit
4. **Check IP Adres**: Verifieer robot IP adres
5. **Herstart Robot**: Probeer robot opnieuw op te starten

## Officiële Unitree Ondersteuning

Voor vragen over je robot variant:
- **Website**: https://www.unitree.com
- **Support**: https://support.unitree.com
- **Email**: Check Unitree website voor contact informatie

## Referenties

- [Go2 Handleiding](./GO2_HANDLEIDING.md)
- [Go2 SDK Referentie](./GO2_SDK_REFERENTIE.md)
- [Project README](../README.md)

