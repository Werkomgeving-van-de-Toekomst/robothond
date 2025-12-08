# Web Search via Fysieke Go2 Robot

Deze guide beschrijft hoe je via de fysieke Go2 robot op internet kunt zoeken en resultaten kunt tonen op een gekoppelde PC.

## Overzicht

Je kunt tegen de robot praten om te zoeken op internet. De robot:
1. Luistert naar je commando
2. Zoekt op internet
3. Toont resultaten op gekoppelde PC display
4. Spreekt resultaten uit (optioneel)

## Snel Starten

### Stap 1: Start Display Server

Open een terminal en start de display server:

```bash
python src/controller_app/display_server.py --port 5001
```

### Stap 2: Open Display in Browser

Open in je browser:
```
http://localhost:5001
```

### Stap 3: Start Voice Control met Robot

```bash
python src/examples/voice_control.py \
    --robot-ip 192.168.123.161 \
    --display-url http://localhost:5001/api \
    --whisper
```

### Stap 4: Praat tegen de Robot

Zeg bijvoorbeeld:
- **"zoek Unitree Go2 robot"**
- **"vind informatie over quadrupeds"**
- **"google reinforcement learning"**

De robot zoekt en toont resultaten op het scherm!

## Complete Setup

### Terminal 1: Display Server

```bash
python src/controller_app/display_server.py --port 5001
```

### Terminal 2: Voice Control

```bash
python src/examples/voice_control.py \
    --robot-ip 192.168.123.161 \
    --display-url http://localhost:5001/api \
    --whisper \
    --whisper-model base
```

### Browser: Display

Open `http://localhost:5001` in je browser.

## Voice Commando's voor Zoeken

### Basis Commando's

- **"zoek [term]"** - Zoek op internet
  - Voorbeeld: "zoek Unitree Go2 robot"
  
- **"vind [term]"** - Zoek op internet
  - Voorbeeld: "vind informatie over AI"
  
- **"google [term]"** - Zoek op internet
  - Voorbeeld: "google machine learning"
  
- **"zoek op internet [term]"** - Zoek op internet
  - Voorbeeld: "zoek op internet quadrupeds"

### Voorbeeld Gesprek

```
Jij: "zoek Unitree Go2 robot"
Robot: "Zoeken naar Unitree Go2 robot"
Robot: "Ik heb 5 resultaten gevonden en getoond op het scherm"
```

Resultaten verschijnen nu op `http://localhost:5001`

## Via API Server

Je kunt ook de API server gebruiken:

### Terminal 1: Display Server

```bash
python src/controller_app/display_server.py --port 5001
```

### Terminal 2: API Server

```bash
python src/controller_app/model_api_server.py --host 0.0.0.0 --port 5000
```

### Terminal 3: Voice Control

```bash
python src/examples/voice_control.py \
    --api http://localhost:5000/api \
    --display-url http://localhost:5001/api \
    --whisper
```

## Netwerk Setup

### Voor PC op Ander Netwerk

Als je display server op een andere PC draait:

```bash
# Op PC met display server
python src/controller_app/display_server.py --host 0.0.0.0 --port 5001

# Op robot computer
python src/examples/voice_control.py \
    --robot-ip 192.168.123.161 \
    --display-url http://192.168.1.100:5001/api \
    --whisper
```

Vervang `192.168.1.100` met het IP adres van de PC met display.

## Integratie met Flows

Je kunt web search ook gebruiken in flows:

```yaml
name: "Zoek en Toon Flow"

actions:
  - name: "Sta op"
    type: stand
    duration: 2.0
    
  - name: "Zoek op internet"
    type: web_search
    params:
      query: "Unitree Go2 robot"
      max_results: 5
      speak_results: true
      show_on_display: true
    
  - name: "Wacht"
    type: wait
    duration: 3.0
```

Voer uit:
```bash
python src/examples/run_flow.py \
    --yaml flows/search_flow.yaml \
    --voice \
    --display-url http://localhost:5001/api
```

## Python API

### Direct Gebruik

```python
from src.unitree_go2.robot import Go2Robot
from src.voice.voice_controller import Go2VoiceController
from src.unitree_go2.web_search import WebSearcher

# Connect robot
robot = Go2Robot(ip_address="192.168.123.161")
robot.connect()

# Setup
searcher = WebSearcher()
voice_controller = Go2VoiceController(
    robot=robot,
    web_searcher=searcher,
    display_api_url="http://localhost:5001/api",
    use_whisper=True
)

# Start luisteren
voice_controller.start_listening()

# Nu kun je zeggen: "zoek Unitree Go2"
```

## Troubleshooting

### Robot hoort commando niet

- Spreek duidelijk en rustig
- Check microfoon permissies
- Gebruik `--whisper` voor betere herkenning
- Test eerst met `listen_once()` om te zien of microfoon werkt

### Geen resultaten op display

- Check of display server draait: `http://localhost:5001`
- Check `--display-url` parameter
- Test met: `curl http://localhost:5001/api/display`
- Check firewall als je netwerk gebruikt

### Zoeken werkt niet

- Check internet verbinding
- Test web searcher apart:
  ```python
  from src.unitree_go2.web_search import WebSearcher
  searcher = WebSearcher()
  results = searcher.search("test")
  print(results)
  ```

### Display server start niet

- Check of poort 5001 beschikbaar is
- Gebruik andere poort: `--port 8080`
- Check firewall instellingen

## Best Practices

1. **Start display eerst**: Zorg dat display server draait voordat je voice control start
2. **Test microfoon**: Test eerst of microfoon werkt
3. **Spreek duidelijk**: Spreek langzaam en duidelijk
4. **Check display**: Houd browser open om resultaten te zien
5. **Netwerk**: Gebruik lokaal netwerk voor beste performance

## Volgende Stappen

1. **Test voice commando's**: Test alle zoek commando's
2. **Custom flows**: Maak flows die zoeken en resultaten tonen
3. **Meerdere displays**: Run meerdere display servers
4. **Voice shortcuts**: Maak shortcuts voor veelgebruikte zoekopdrachten

