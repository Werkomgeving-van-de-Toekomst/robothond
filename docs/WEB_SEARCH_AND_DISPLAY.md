# Web Search en Display voor Go2 Robot

De Go2 robot kan informatie opzoeken op internet en de resultaten tonen op een gekoppelde PC met scherm.

## Overzicht

Het systeem bestaat uit:
- **Web Searcher**: Zoekt informatie op internet (DuckDuckGo, Google, Bing)
- **Display Server**: Web server die resultaten toont op een PC/scherm
- **Flow Integratie**: Gebruik web search in robot flows

## Snel Starten

### Stap 1: Start Display Server

Open een terminal en start de display server:

```bash
python src/controller_app/display_server.py --port 5001
```

De server draait nu op `http://localhost:5001`

### Stap 2: Open Display in Browser

Open in je browser:
```
http://localhost:5001
```

Je ziet nu het Go2 Robot Display scherm.

### Stap 3: Zoek en Toon

```bash
python src/examples/search_and_display.py --query "Unitree Go2 robot" --display-url http://localhost:5001/api
```

De zoekresultaten worden nu getoond op het scherm!

## Display Server

### Starten

```bash
# Standaard poort 5001
python src/controller_app/display_server.py

# Custom poort
python src/controller_app/display_server.py --port 8080

# Op alle interfaces (voor netwerk toegang)
python src/controller_app/display_server.py --host 0.0.0.0 --port 5001
```

### API Endpoints

#### GET `/api/display`
Haal huidige display content op.

#### POST `/api/display`
Update display content.

```json
{
  "title": "Titel",
  "content": "Inhoud",
  "type": "text"
}
```

#### POST `/api/display/text`
Stel tekst in.

```json
{
  "text": "Dit is de tekst"
}
```

#### POST `/api/display/search`
Toon zoekresultaten.

```json
{
  "query": "zoekterm",
  "results": [
    {
      "title": "Titel",
      "url": "https://example.com",
      "snippet": "Beschrijving..."
    }
  ]
}
```

#### POST `/api/display/clear`
Wis display.

## Web Search

### Python API

```python
from src.unitree_go2.web_search import WebSearcher

# Maak searcher
searcher = WebSearcher(search_engine="duckduckgo")

# Zoek
results = searcher.search("Unitree Go2", max_results=5)

# Print resultaten
for result in results:
    print(f"{result['title']}")
    print(f"  {result['url']}")
    print(f"  {result['snippet']}")
```

### Search Engines

- **DuckDuckGo** (aanbevolen): Geen API key nodig
- **Google**: Vereist API key (Custom Search API)
- **Bing**: Vereist API key

### Samenvatting

```python
summary = searcher.search_and_summarize("Unitree Go2", max_results=3)
print(summary)
```

## Flow Integratie

### Web Search Actie

```yaml
- name: "Zoek op internet"
  type: web_search
  params:
    query: "Unitree Go2 robot"
    max_results: 5
    speak_results: true  # Spreek resultaten uit
    show_on_display: true  # Toon op display
```

### Display Actie

```yaml
- name: "Toon op display"
  type: display
  params:
    title: "Titel"
    content: "Inhoud"
    display_type: text
```

### Voorbeeld Flow

```bash
python src/examples/run_flow.py --yaml flows/search_flow.yaml --voice
```

## Complete Voorbeeld

### Terminal 1: Start Display Server

```bash
python src/controller_app/display_server.py --port 5001
```

### Terminal 2: Run Search Flow

```bash
python src/examples/run_flow.py \
    --yaml flows/search_flow.yaml \
    --voice \
    --display-url http://localhost:5001/api
```

### Browser: Bekijk Resultaten

Open `http://localhost:5001` in je browser.

## Python Script Voorbeeld

```python
from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.flow_executor import FlowExecutor
from src.unitree_go2.web_search import WebSearcher
from src.voice.voice_controller import Go2VoiceController
import requests

# Connect robot
robot = Go2Robot(ip_address="192.168.123.161")
robot.connect()

# Setup
searcher = WebSearcher()
voice_controller = Go2VoiceController(robot=robot)
executor = FlowExecutor(
    robot=robot,
    voice_controller=voice_controller,
    web_searcher=searcher,
    display_api_url="http://localhost:5001/api"
)

# Zoek en toon
query = "Unitree Go2 robot"
results = searcher.search(query, max_results=5)

# Toon op display
requests.post(
    "http://localhost:5001/api/display/search",
    json={"query": query, "results": results}
)

# Spreek uit
summary = searcher.search_and_summarize(query, max_results=3)
voice_controller.speak(summary)

robot.disconnect()
```

## Netwerk Setup

### Lokale PC

Display server op localhost:
```bash
python src/controller_app/display_server.py --host 127.0.0.1 --port 5001
```

### Netwerk PC

Voor toegang vanaf andere apparaten:
```bash
python src/controller_app/display_server.py --host 0.0.0.0 --port 5001
```

Vervang `localhost` met het IP adres van de PC:
```python
display_api_url = "http://192.168.1.100:5001/api"
```

### Firewall

Zorg dat poort 5001 open is in firewall als je netwerk toegang wilt.

## Custom Display

Je kunt de display HTML aanpassen in `src/controller_app/display_server.py`.

De template is in de `DISPLAY_TEMPLATE` variabele.

## Troubleshooting

### Display server start niet

- Check of poort 5001 beschikbaar is
- Gebruik andere poort: `--port 8080`
- Check firewall instellingen

### Geen zoekresultaten

- Check internet verbinding
- DuckDuckGo werkt zonder API key
- Voor Google/Bing: configureer API keys

### Display toont niets

- Check of display server draait
- Check URL: `http://localhost:5001/api`
- Check browser console voor errors
- Test met: `curl http://localhost:5001/api/display`

### Netwerk toegang werkt niet

- Check firewall
- Gebruik `--host 0.0.0.0`
- Check IP adres van PC
- Test met `curl http://<PC_IP>:5001/api/display`

## Geavanceerd Gebruik

### Custom Search Engine

```python
class CustomSearcher(WebSearcher):
    def _search_custom(self, query, max_results):
        # Implementeer custom search
        pass

searcher = CustomSearcher()
```

### Display Updates

```python
import requests

# Update tekst
requests.post("http://localhost:5001/api/display/text", json={
    "text": "Nieuwe tekst"
})

# Update met zoekresultaten
requests.post("http://localhost:5001/api/display/search", json={
    "query": "zoekterm",
    "results": [...]
})
```

### Auto-refresh

De display pagina refresht automatisch elke 2 seconden.

Je kunt dit aanpassen in de JavaScript in `display_server.py`.

## Volgende Stappen

1. **Integreer met voice**: Gebruik voice commando's om te zoeken
2. **Custom flows**: Maak flows die zoeken en resultaten tonen
3. **Meerdere displays**: Run meerdere display servers op verschillende poorten
4. **Custom styling**: Pas HTML/CSS aan voor jouw gebruik

