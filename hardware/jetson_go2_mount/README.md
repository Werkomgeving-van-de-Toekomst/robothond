# Jetson AGX Orin Mount voor Go2 Robot

3D-printbare mount om een Jetson AGX Orin Developer Kit te bevestigen op de Unitree Go2 robot.

## Ontwerp Overzicht

```
        ┌─────────────────────────────────────┐
        │      Jetson AGX Orin Mount          │
        │  ┌─────────────────────────────┐    │
        │  │    ○ ─────────────── ○      │    │  ← Jetson standoffs
        │  │    │  ░░░░░░░░░░░░░  │      │    │
        │  │    │  ░ Ventilatie ░  │      │    │  ← Ventilatie gaten
        │  │    │  ░░░░░░░░░░░░░  │      │    │
        │  │    ○ ─────────────── ○      │    │
        │  └─────────────────────────────┘    │
        │                                      │
        │  ┌──────────┐                        │
        │  │Powerbank │  ← Optionele houder   │
        │  │ Houder   │                        │
        │  └──────────┘                        │
        └──○────────────────────────────○─────┘
           │                            │
           └── Go2 mounting tabs ───────┘
```

## Specificaties

| Component | Afmeting |
|-----------|----------|
| Totale breedte | 160 mm (+ powerbank: 250 mm) |
| Totale diepte | 140 mm |
| Hoogte (zonder Jetson) | ~23 mm |
| Gewicht (geschat) | ~150-200 gram |

### Compatibiliteit

- **Robot**: Unitree Go2 (alle varianten)
- **Computer**: NVIDIA Jetson AGX Orin Developer Kit (110x110mm)
- **Powerbank**: Past powerbanks tot 80x160x30mm

## Bestanden

| Bestand | Beschrijving |
|---------|--------------|
| `jetson_go2_mount.scad` | OpenSCAD bronbestand (parametrisch) |
| `jetson_go2_mount.stl` | Print-ready STL (genereer vanuit .scad) |

## Print Instructies

### Aanbevolen Instellingen

| Parameter | Waarde | Opmerking |
|-----------|--------|-----------|
| **Materiaal** | PETG of ABS | PLA is te zwak voor deze toepassing |
| **Nozzle** | 0.4 mm | Standaard |
| **Layer hoogte** | 0.2 mm | Balans tussen sterkte en snelheid |
| **Infill** | 40-50% | Hogere infill = sterker |
| **Infill patroon** | Gyroid of Cubic | Beste sterkte |
| **Wanden** | 3-4 | Extra sterkte |
| **Top/Bottom layers** | 4-5 | Stevige oppervlakken |
| **Supports** | Ja | Voor mounting tabs |
| **Support type** | Tree supports | Makkelijker te verwijderen |
| **Bed adhesion** | Brim (8mm) | Voorkomt warping |
| **Print temp** | PETG: 240°C / ABS: 250°C | Check filament specs |
| **Bed temp** | PETG: 80°C / ABS: 100°C | |

### Print Oriëntatie

Print met de **platte kant naar beneden** (mounting tabs naar boven gericht tijdens print).

```
Print bed:
═══════════════════════════════════
    ┌─────────────────────────┐
    │                         │
    │    Basis plaat          │  ← Plat op bed
    │                         │
    └─────────────────────────┘
         ↑ Standoffs groeien omhoog
```

### Print Tijd

- **Zonder powerbank mount**: ~4-5 uur
- **Met powerbank mount**: ~6-8 uur

## STL Genereren

### Optie 1: OpenSCAD GUI

1. Open `jetson_go2_mount.scad` in OpenSCAD
2. Pas parameters aan indien nodig
3. Klik `Design` → `Render` (F6)
4. Klik `File` → `Export` → `Export as STL`

### Optie 2: Command Line

```bash
# Installeer OpenSCAD (macOS)
brew install openscad

# Genereer STL
openscad -o jetson_go2_mount.stl jetson_go2_mount.scad

# Met custom parameters (bijv. zonder powerbank mount)
openscad -o jetson_go2_mount_no_powerbank.stl \
    -D 'include_powerbank_mount=false' \
    jetson_go2_mount.scad
```

## Aanpassingen

Het OpenSCAD bestand is volledig parametrisch. Je kunt de volgende variabelen aanpassen:

```openscad
// Jetson afmetingen (pas aan voor andere Jetson modellen)
jetson_width = 110;
jetson_depth = 110;

// Standoff hoogte (meer ruimte voor ventilatie)
standoff_height = 15;  // Verhoog naar 20 voor betere koeling

// Powerbank houder aan/uit
include_powerbank_mount = true;  // Zet op false om uit te schakelen

// Powerbank afmetingen (pas aan voor jouw powerbank)
powerbank_width = 80;
powerbank_depth = 160;
powerbank_height = 30;
```

## Montage

### Benodigdheden

| Item | Aantal | Specificatie |
|------|--------|--------------|
| M3 x 8mm schroeven | 4 | Voor Jetson bevestiging |
| M3 moeren | 4 | Optioneel (standoffs hebben gaten) |
| M4 of M5 schroeven | 4 | Voor Go2 bevestiging (check Go2 specs) |
| Korte Ethernet kabel | 1 | 30-50cm |
| Velcro straps | 2 | Voor powerbank (optioneel) |

### Montage Stappen

1. **Print de mount** volgens bovenstaande instructies
2. **Verwijder supports** en schuur eventuele ruwe randen
3. **Test fit** de Jetson op de standoffs
4. **Bevestig Jetson** met M3 schroeven
5. **Plaats op Go2** en bevestig met M4/M5 schroeven in de tabs
6. **Route kabels** door de kabel slots
7. **Bevestig powerbank** met velcro straps (indien van toepassing)

### Kabel Routing

```
                    ┌─────────────────┐
                    │     Jetson      │
     Power ←────────┤                 ├────────→ Ethernet naar Go2
     (USB-C)        │                 │
                    └─────────────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │   Go2 Robot     │
                    └─────────────────┘
```

## Veiligheid

⚠️ **Let op:**

- **Gewicht**: Jetson + mount + powerbank = ~2-3 kg. Blijf onder Go2's 8kg payload limiet.
- **Zwaartepunt**: Monteer zo laag mogelijk op de robot
- **Kabels**: Zorg dat kabels niet in de poten kunnen komen
- **Ventilatie**: Blokkeer de Jetson ventilator niet
- **Temperatuur**: Monitor Jetson temperatuur tijdens gebruik

## Alternatieve Mounts

Voor andere Jetson modellen, pas de parameters aan:

| Jetson Model | Breedte | Diepte | Hoogte |
|--------------|---------|--------|--------|
| AGX Orin Dev Kit | 110 mm | 110 mm | 71.65 mm |
| AGX Orin 32GB | 100 mm | 87 mm | 40 mm |
| Orin NX | 100 mm | 87 mm | 35 mm |
| Orin Nano | 100 mm | 79 mm | 30 mm |

## Referenties

- [Unitree Go2 Payload Specificaties](https://support.unitree.com/home/en/developer/Payload)
- [NVIDIA Jetson AGX Orin Datasheet](https://developer.nvidia.com/embedded/jetson-agx-orin)
- [OpenSCAD Documentatie](https://openscad.org/documentation.html)

## Licentie

MIT License - Vrij te gebruiken en aan te passen.

