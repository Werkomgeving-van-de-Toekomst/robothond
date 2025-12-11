# Go2 Power Outlet voor Jetson AGX Orin

Complete handleiding voor het gebruik van de Unitree Go2 power outlet om een Jetson AGX Orin van stroom te voorzien.

## Overzicht

De Unitree Go2 robot heeft een **payload power outlet** die je kunt gebruiken om externe apparaten van stroom te voorzien. Dit is ideaal voor het voeden van een Jetson AGX Orin zonder externe powerbank.

## Power Specificaties

### Go2 Power Outlet

| Specificatie | Waarde | Bron |
|--------------|--------|------|
| **Output voltage** | 28-33.6V DC | Unitree Go2 specificaties |
| **Max current** | ~2-3A (afhankelijk van model) | Check Go2 documentatie |
| **Max power** | ~60-100W | Afhankelijk van robot configuratie |
| **Connector type** | DC barrel jack of terminal block | Model afhankelijk |
| **Locatie** | Payload area (rug van robot) | |

### Jetson AGX Orin Requirements

| Specificatie | Waarde |
|--------------|--------|
| **Input voltage** | 9-20V DC (of USB-C PD) |
| **Power consumption** | 15-75W (afhankelijk van mode) |
| **Peak power** | ~100W bij maximale belasting |
| **Connector** | DC barrel jack (5.5x2.5mm) of USB-C |

### Voltage Conversie Vereist

```
Go2 Output:  28-33.6V DC
                ↓
         [DC-DC Converter]
                ↓
Jetson Input: 12V of 19V DC
```

## DC-DC Converter Selectie

Je hebt een **step-down (buck) converter** nodig om van 28-33.6V naar 12V of 19V te converteren.

### Aanbevolen Converters

| Model | Input | Output | Max Power | Opmerkingen |
|-------|-------|--------|-----------|-------------|
| **DROK DC-DC Buck** | 6-40V | 12V/5A | 60W | Goedkoop, betrouwbaar |
| **Mean Well SD-100A-12** | 18-36V | 12V/8.3A | 100W | Professioneel, efficiënt |
| **Vicor VI-200** | 18-36V | 12V/16A | 200W | Overkill, zeer efficiënt |
| **Custom 19V converter** | 24-36V | 19V/5A | 95W | Voor originele Jetson adapter |

### Converter Specificaties

**Minimale vereisten:**
- **Input voltage range**: 24-36V (om 28-33.6V te accommoderen)
- **Output voltage**: 12V of 19V (afhankelijk van Jetson configuratie)
- **Output current**: Minimaal 5A (voor 60W+)
- **Efficiency**: >85% (minder warmte, langer runtime)
- **Protection**: Overcurrent, overvoltage, short-circuit

### Aanbevolen: Mean Well SD-100A-12

```
Specificaties:
- Input: 18-36V DC
- Output: 12V @ 8.3A (100W)
- Efficiency: 90%
- Size: 101 x 51 x 30mm
- Weight: ~200g
- Prijs: ~€30-40
```

**Waarom deze converter:**
- ✅ Past perfect in voltage range
- ✅ Genoeg power voor Jetson (zelfs bij piekbelasting)
- ✅ Hoge efficiency = minder warmte
- ✅ Betrouwbaar merk
- ✅ Compact formaat

## Aansluitinstructies

### Stap 1: Locate Go2 Power Outlet

De power outlet bevindt zich in de **payload area** op de rug van de Go2:

```
        ┌─────────────────────┐
        │                     │
        │    Go2 Robot        │
        │                     │
        │  ┌───────────────┐ │
        │  │ Payload Area  │ │
        │  │               │ │
        │  │ [Power Out]   │ │ ← Power outlet hier
        │  │ [Ethernet]    │ │
        │  │ [USB]         │ │
        │  └───────────────┘ │
        └─────────────────────┘
```

**Check je Go2 model documentatie** voor exacte locatie en connector type.

### Stap 2: Aansluitingen Maken

#### Optie A: Terminal Block (Als beschikbaar)

```
Go2 Power Outlet          DC-DC Converter
┌──────────────┐          ┌──────────────┐
│  +28-33.6V   │──────────►│  VIN+        │
│              │           │              │
│  GND         │──────────►│  VIN-        │
└──────────────┘           └──────────────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │  VOUT+ (12V) │───► Jetson VIN+
                            │              │
                            │  VOUT- (GND) │───► Jetson GND
                            └──────────────┘
```

#### Optie B: DC Barrel Jack

Als de Go2 een DC barrel jack heeft, gebruik een **adapter kabel**:

```
Go2 DC Jack → Adapter → DC-DC Converter → Jetson
```

### Stap 3: DC-DC Converter Configureren

**Voor Mean Well SD-100A-12:**

1. **Stel output voltage in** (meestal 12V, soms 19V)
   - Gebruik potentiometer op converter
   - Meet met multimeter voor verificatie

2. **Bevestig converter** op mount of direct op robot
   - Gebruik isolerende standoffs
   - Zorg voor ventilatie

3. **Verbind kabels:**
   ```
   Go2 + → Converter VIN+
   Go2 - → Converter VIN-
   Converter VOUT+ → Jetson VIN+
   Converter VOUT- → Jetson GND
   ```

### Stap 4: Jetson Aansluiten

**Optie 1: Direct DC Input (Aanbevolen)**

De Jetson AGX Orin heeft een **DC barrel jack** (5.5x2.5mm):

```
Converter 12V Output → DC Barrel Jack → Jetson DC Input
```

**Optie 2: Via Carrier Board**

Als je een carrier board gebruikt, sluit aan op de **power input terminals**.

### Stap 5: Testen

```bash
# 1. Check Go2 power output (met multimeter)
#    Moet 28-33.6V DC zijn

# 2. Check converter output
#    Moet 12V (of 19V) zijn

# 3. Sluit Jetson aan en start op
#    Monitor voltage tijdens boot

# 4. Check Jetson power status
sudo tegrastats  # Toont voltage en current
```

## Veiligheid

### ⚠️ Belangrijke Waarschuwingen

1. **Polariteit**: Controleer altijd + en - voordat je aansluit!
   - Verkeerde polariteit kan Jetson permanent beschadigen

2. **Voltage**: Meet altijd eerst met multimeter
   - Go2 output: 28-33.6V
   - Converter output: 12V of 19V

3. **Current**: Zorg dat converter genoeg current kan leveren
   - Jetson kan pieken tot 75W trekken
   - Converter moet minimaal 5-6A kunnen leveren

4. **Fuses**: Overweeg zekeringen toe te voegen
   ```
   Go2 → [Fuse 3A] → Converter → [Fuse 5A] → Jetson
   ```

5. **Isolatie**: Isoleer alle verbindingen
   - Gebruik heat shrink tubing
   - Voorkom kortsluiting

6. **Ventilatie**: Converter genereert warmte
   - Zorg voor luchtstroom
   - Monteer niet direct tegen Jetson

### Veiligheidschecklist

- [ ] Multimeter gebruikt om voltages te verifiëren
- [ ] Polarity gecontroleerd (+ en -)
- [ ] Converter rated voor minimaal 60W
- [ ] Alle verbindingen geïsoleerd
- [ ] Converter heeft voldoende ventilatie
- [ ] Fuses geïnstalleerd (aanbevolen)
- [ ] Eerste test met robot uit (alleen converter)
- [ ] Jetson boot succesvol

## Mount Aanpassingen

De 3D print mount kan worden aangepast om de DC-DC converter te accommoderen:

### Converter Mount Opties

**Optie 1: Converter naast Jetson**

```
┌─────────────────────────────────────┐
│      Jetson AGX Orin Mount           │
│  ┌─────────────┐  ┌─────────────┐  │
│  │   Jetson    │  │   Converter  │  │
│  │             │  │   (Mean Well)│  │
│  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────┘
```

**Optie 2: Converter onder Jetson**

```
┌─────────────────────────────────────┐
│      Jetson AGX Orin                 │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │   DC-DC Converter           │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

### OpenSCAD Aanpassingen

Pas `jetson_go2_mount.scad` aan:

```openscad
// Voeg converter mount toe
converter_width = 101;
converter_depth = 51;
converter_height = 30;

module converter_mount() {
    // Converter mounting plate
    translate([plate_width/2 + jetson_width/2 + 10, 
               (plate_depth - converter_depth)/2, 0]) {
        difference() {
            cube([converter_width + 4, converter_depth + 4, plate_thickness]);
            translate([2, 2, -1])
                cube([converter_width, converter_depth, plate_thickness + 2]);
        }
        
        // Mounting holes voor converter
        for (x = [10, converter_width - 10]) {
            for (y = [10, converter_depth - 10]) {
                translate([x, y, plate_thickness])
                    cylinder(h = 5, d = 3, $fn = 24);
            }
        }
    }
}
```

## Troubleshooting

### Probleem: Jetson start niet op

**Oplossingen:**
1. Check voltage op converter output (moet 12V zijn)
2. Check polarity (+ en -)
3. Check current draw (Jetson kan veel vragen bij boot)
4. Probeer met externe powerbank eerst (isolatie test)

### Probleem: Converter wordt te heet

**Oplossingen:**
1. Check efficiency rating (moet >85% zijn)
2. Zorg voor betere ventilatie
3. Overweeg grotere converter (meer headroom)
4. Check of converter niet overbelast wordt

### Probleem: Voltage instabiliteit

**Oplossingen:**
1. Check Go2 power output stabiliteit
2. Voeg grote capacitor toe aan converter output
3. Gebruik betere kwaliteit converter
4. Check kabel lengte (korter = beter)

### Probleem: Jetson reboot tijdens gebruik

**Oplossingen:**
1. Converter levert niet genoeg current
2. Upgrade naar converter met meer power headroom
3. Check voor voltage drops tijdens piekbelasting
4. Monitor Jetson power consumption met `tegrastats`

## Power Monitoring

### Jetson Power Status

```bash
# Real-time power monitoring
sudo tegrastats

# Output toont:
# - Voltage (V)
# - Current (A)
# - Power (W)
# - Temperature
```

### Converter Monitoring

Gebruik een **multimeter** of **power meter** om te monitoren:
- Input voltage (van Go2)
- Output voltage (naar Jetson)
- Current draw
- Efficiency

## Alternatieve Configuraties

### Configuratie 1: 12V Output

```
Go2 (28-33.6V) → Converter (12V) → Jetson (12V input)
```

**Voordelen:**
- Standaard voltage
- Veel converters beschikbaar
- Goede efficiency

### Configuratie 2: 19V Output

```
Go2 (28-33.6V) → Converter (19V) → Jetson (19V input)
```

**Voordelen:**
- Minder current nodig (bij zelfde power)
- Minder voltage drop in kabels
- Kan originele Jetson adapter simuleren

### Configuratie 3: USB-C PD Trigger

```
Go2 (28-33.6V) → Converter (12V) → USB-C PD Trigger (20V) → Jetson USB-C
```

**Voordelen:**
- Gebruik Jetson USB-C port
- Geen DC barrel jack nodig
- Moderne oplossing

## Kosten Overzicht

| Item | Prijs | Opmerkingen |
|------|-------|-------------|
| Mean Well SD-100A-12 | €30-40 | Aanbevolen converter |
| DROK Buck Converter | €10-15 | Budget optie |
| DC Barrel Jack | €2-5 | Connector |
| Kabel & Connectors | €5-10 | Aansluitmateriaal |
| Fuses & Holder | €5 | Veiligheid |
| **Totaal** | **€50-70** | Professionele setup |

📦 **Zie [BESTELLIJST_POWER_SETUP.md](BESTELLIJST_POWER_SETUP.md) voor complete bestellijst met specifieke producten en webshops!**

## Vergelijking: Powerbank vs Go2 Power

| Aspect | Powerbank | Go2 Power Outlet |
|--------|-----------|------------------|
| **Gewicht** | +500g-1kg | +200g (converter) |
| **Runtime** | 2-4 uur | Onbeperkt (zolang robot aan) |
| **Kosten** | €100-200 | €50-70 |
| **Complexiteit** | Laag | Medium |
| **Setup tijd** | 5 min | 30-60 min |
| **Onderhoud** | Laden | Geen |

**Conclusie**: Go2 power outlet is beter voor **lange sessies** en **gewichtsbesparing**, maar vereist meer technische kennis.

## Referenties

- [Unitree Go2 Payload Documentatie](https://support.unitree.com/home/en/developer/Payload)
- [NVIDIA Jetson AGX Orin Power Guide](https://developer.nvidia.com/embedded/jetson-agx-orin)
- [Mean Well SD-100A Datasheet](https://www.meanwell.com/productPdf.aspx?i=488)

## Zie Ook

- **[BESTELLIJST_POWER_SETUP.md](BESTELLIJST_POWER_SETUP.md)** - **Complete bestellijst met specifieke producten** ⭐
- [JETSON_GO2_MONTAGE.md](JETSON_GO2_MONTAGE.md) - Complete montage handleiding
- [JETSON_AGX_ORIN_VERBINDING.md](JETSON_AGX_ORIN_VERBINDING.md) - Netwerk setup

