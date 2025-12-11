# Go2 Robot Flows

Deze directory bevat voorgedefinieerde actie-sequenties (flows) voor de Unitree Go2 robot.

## Beschikbare Flows

| Flow | Beschrijving |
|------|--------------|
| `welcome_flow.yaml` | Welkom routine - loop naar persoon en groet |
| `custom_flow_example.yaml` | Voorbeeld met verschillende actie types |
| `search_flow.yaml` | Internet zoeken en resultaten tonen |
| `dance_flow.yaml` | Dans routines |
| `tricks_flow.yaml` | Poses en tricks demonstratie |
| `acrobatics_flow.yaml` | Acrobatiek (⚠️ vereist ruimte!) |
| `walk_styles_flow.yaml` | Verschillende loopstijlen |

## Flow Uitvoeren

```bash
# Via run_flow.py script
python src/examples/run_flow.py --yaml flows/welcome_flow.yaml

# Met voice controller
python src/examples/run_flow.py --yaml flows/dance_flow.yaml --voice

# Met Whisper spraakherkenning
python src/examples/run_flow.py --yaml flows/tricks_flow.yaml --voice --whisper
```

## Beschikbare Actie Types

### Basis Beweging
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `stand` | Rechtop staan | `duration` |
| `sit` | Ga liggen (StandDown) | `duration` |
| `stand_down` | Ga liggen | `duration` |
| `move` | Beweeg met snelheid | `vx`, `vy`, `vyaw`, `duration` |
| `move_to` | Beweeg naar positie | `x`, `y`, `yaw`, `speed` |
| `rotate` | Draai op de plaats | `angle` (graden), `speed` |
| `stop` | Stop beweging | `duration` |
| `damp` | Motoren uit | `duration` |
| `balance_stand` | Gebalanceerd staan | `duration` |
| `recovery_stand` | Herstel na val | `duration` |

### Poses & Tricks
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `sit_down` | Echte zit positie | `duration` |
| `rise_sit` | Sta op vanuit zit | `duration` |
| `hello` | Zwaai/groet | `duration` |
| `stretch` | Rek beweging | `duration` |
| `heart` | Hart gebaar | `duration` |
| `scrape` | Krab beweging | `duration` |
| `content` | Tevreden beweging | `duration` |
| `pose` | Pose modus | `enabled` |

### Dansen
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `dance1` | Dans routine 1 | `duration` |
| `dance2` | Dans routine 2 | `duration` |

### Acrobatiek ⚠️
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `front_flip` | Salto voorwaarts | `duration` |
| `back_flip` | Salto achterwaarts | `duration` |
| `left_flip` | Salto naar links | `duration` |
| `front_jump` | Spring vooruit | `duration` |
| `front_pounce` | Duik vooruit | `duration` |
| `hand_stand` | Handstand | `enabled`, `duration` |

### Loopstijlen
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `free_walk` | Vrije loop | `duration` |
| `static_walk` | Statische loop | `duration` |
| `trot_run` | Draf/ren | `duration` |
| `classic_walk` | Klassieke loop | `enabled` |
| `walk_upright` | Rechtop lopen | `enabled`, `duration` |
| `cross_step` | Kruis-stap | `enabled`, `duration` |

### Speciale Modi
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `free_bound` | Vrij springen | `enabled`, `duration` |
| `free_jump` | Vrij springen | `enabled`, `duration` |
| `free_avoid` | Obstakel vermijding | `enabled`, `duration` |

### Instellingen
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `speed_level` | Snelheidsniveau | `level` (0-2) |
| `euler` | Lichaam oriëntatie | `roll`, `pitch`, `yaw` |
| `switch_joystick` | Joystick aan/uit | `enabled` |
| `auto_recovery` | Auto herstel | `enabled` |
| `switch_avoid_mode` | Wissel vermijd modus | - |

### Utility
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `wait` | Wacht | `duration` |
| `speak` | Print tekst | `text` |
| `voice_speak` | Spreek tekst | `text` |
| `web_search` | Zoek op internet | `query`, `max_results`, `speak_results` |
| `display` | Toon op display | `title`, `content`, `display_type` |

### Flow Controle
| Type | Beschrijving | Parameters |
|------|--------------|------------|
| `condition` | Conditionele actie | `condition`, `actions` |
| `loop` | Herhaal acties | `count`, `actions` |
| `parallel` | Parallelle acties | `actions` |

## Eigen Flow Maken

```yaml
# mijn_flow.yaml
name: "Mijn Custom Flow"
description: "Beschrijving van de flow"

actions:
  - name: "Actie naam"
    type: stand
    duration: 2.0
    
  - name: "Beweging"
    type: move
    params:
      vx: 0.3
      vy: 0.0
      vyaw: 0.0
    duration: 3.0
    
  - name: "Spreek"
    type: voice_speak
    params:
      text: "Hallo wereld!"
```

## Veiligheid

⚠️ **Let op bij acrobatiek:**
- Minimaal 3 meter vrije ruimte rondom de robot
- Geen obstakels in de buurt
- Zachte ondergrond aanbevolen
- Houd afstand tijdens uitvoering
- Test eerst met minder gevaarlijke bewegingen

