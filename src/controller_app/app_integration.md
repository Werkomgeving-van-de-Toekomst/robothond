# Unitree Go App Integratie met RL Modellen

Deze guide beschrijft hoe je de officiële Unitree Go app kunt gebruiken om RL modellen te selecteren en te gebruiken.

## Overzicht

De Unitree Go app ([App Store](https://apps.apple.com/us/app/unitree-go-embodied-ai/id1579283821)) heeft een "Programming" functie die we kunnen gebruiken om RL modellen te selecteren. We maken een API server die als brug dient tussen de app en onze RL modellen.

## Setup

### Stap 1: Installeer Dependencies

```bash
conda activate pybullet  # Of je normale venv
pip install flask flask-cors
```

### Stap 2: Start API Server

```bash
python src/controller_app/model_api_server.py --host 0.0.0.0 --port 5000
```

De server draait nu op `http://<jouw-ip>:5000`

### Stap 3: Vind je IP Adres

```bash
# Op macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Of gebruik
hostname -I
```

Noteer dit IP adres - je hebt het nodig voor de app configuratie.

## API Endpoints

### Model Beheer

#### Lijst Modellen
```
GET http://<server-ip>:5000/api/models
```

Response:
```json
{
  "status": "ok",
  "models": [
    {
      "name": "go2_rl",
      "path": "models/go2_rl/best_model/best_model.zip",
      "type": "walking",
      "config": {}
    },
    {
      "name": "go2_stairs",
      "path": "models/go2_stairs/best_model/best_model.zip",
      "type": "stairs",
      "config": {
        "num_steps": 5,
        "step_height": 0.15,
        "step_depth": 0.25
      }
    }
  ],
  "count": 2
}
```

#### Laad Model
```
POST http://<server-ip>:5000/api/models/go2_rl/load
```

#### Activeer Model
```
POST http://<server-ip>:5000/api/models/go2_rl/activate
```

### Robot Control

#### Connect met Robot
```
POST http://<server-ip>:5000/api/robot/connect
Content-Type: application/json

{
  "ip_address": "192.168.123.161",
  "port": 8080
}
```

#### Start RL Control
```
POST http://<server-ip>:5000/api/control/start
```

#### Stop RL Control
```
POST http://<server-ip>:5000/api/control/stop
```

#### Robot Status
```
GET http://<server-ip>:5000/api/robot/status
```

## Integratie met Unitree Go App

### Optie 1: Via Programming Functie

De Unitree Go app heeft een "Programming" functie. Je kunt deze gebruiken om API calls te maken:

1. Open de Unitree Go app
2. Ga naar "Features" → "Programming"
3. Maak een nieuw programma
4. Gebruik HTTP requests om modellen te selecteren

**Voorbeeld Programma** (pseudo-code voor app):
```
1. HTTP GET naar /api/models
2. Toon lijst van modellen
3. Gebruiker selecteert model
4. HTTP POST naar /api/models/<name>/load
5. HTTP POST naar /api/models/<name>/activate
6. HTTP POST naar /api/control/start
```

### Optie 2: Via Custom Web Interface

Maak een simpele web interface die de app kan openen:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Go2 RL Model Selector</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>Selecteer RL Model</h1>
    <div id="models"></div>
    <button onclick="loadModels()">Ververs Modellen</button>
    
    <script>
    const API_BASE = 'http://<server-ip>:5000/api';
    
    async function loadModels() {
        const response = await fetch(`${API_BASE}/models`);
        const data = await response.json();
        
        const modelsDiv = document.getElementById('models');
        modelsDiv.innerHTML = '';
        
        data.models.forEach(model => {
            const button = document.createElement('button');
            button.textContent = model.name;
            button.onclick = () => activateModel(model.name);
            modelsDiv.appendChild(button);
        });
    }
    
    async function activateModel(name) {
        await fetch(`${API_BASE}/models/${name}/load`, {method: 'POST'});
        await fetch(`${API_BASE}/models/${name}/activate`, {method: 'POST'});
        await fetch(`${API_BASE}/control/start`, {method: 'POST'});
        alert(`Model ${name} geactiveerd!`);
    }
    
    loadModels();
    </script>
</body>
</html>
```

### Optie 3: Via Shortcuts App (iOS)

Je kunt iOS Shortcuts gebruiken om modellen te selecteren:

1. Open Shortcuts app
2. Maak nieuwe shortcut
3. Voeg "Get Contents of URL" toe
4. Stel URL in naar API endpoint
5. Voeg "Show Notification" toe voor feedback

**Voorbeeld Shortcut**:
- URL: `http://<server-ip>:5000/api/models/go2_rl/activate`
- Method: POST
- Show notification: "Model geactiveerd"

## Gebruik Scenario's

### Scenario 1: Wissel tussen Modellen

```bash
# Via curl (test eerst)
curl -X POST http://localhost:5000/api/models/go2_rl/activate
curl -X POST http://localhost:5000/api/control/start

# Wissel naar ander model
curl -X POST http://localhost:5000/api/models/go2_stairs/activate
```

### Scenario 2: Automatisch Model Selecteren

Maak een script dat modellen automatisch wisselt:

```python
import requests
import time

API_BASE = "http://localhost:5000/api"

models = ["go2_rl", "go2_stairs"]

for model_name in models:
    # Activeer model
    requests.post(f"{API_BASE}/models/{model_name}/activate")
    requests.post(f"{API_BASE}/control/start")
    
    # Run voor 30 seconden
    time.sleep(30)
    
    # Stop
    requests.post(f"{API_BASE}/control/stop")
```

## Veiligheid

⚠️ **BELANGRIJK**:

1. **Firewall**: Beperk toegang tot API server (alleen lokaal netwerk)
2. **Authentication**: Overweeg authenticatie toe te voegen voor productie
3. **HTTPS**: Gebruik HTTPS in productie
4. **Rate Limiting**: Voeg rate limiting toe om misbruik te voorkomen

## Troubleshooting

### App kan server niet bereiken

- Check of server draait: `curl http://localhost:5000/api/health`
- Check firewall instellingen
- Verifieer dat app en server opzelfde netwerk zitten
- Check IP adres van server

### Model laadt niet

- Verifieer model pad bestaat
- Check model bestand is geldig
- Check robot is verbonden

### Control start niet

- Verifieer model is geactiveerd
- Check robot is verbonden
- Check control is niet al actief

## Voorbeelden

### Python Client

```python
import requests

API_BASE = "http://localhost:5000/api"

# Lijst modellen
response = requests.get(f"{API_BASE}/models")
models = response.json()["models"]
print(f"Beschikbare modellen: {[m['name'] for m in models]}")

# Connect robot
requests.post(f"{API_BASE}/robot/connect", json={
    "ip_address": "192.168.123.161"
})

# Laad en activeer model
model_name = "go2_rl"
requests.post(f"{API_BASE}/models/{model_name}/load")
requests.post(f"{API_BASE}/models/{model_name}/activate")

# Start control
requests.post(f"{API_BASE}/control/start")
```

### cURL Voorbeelden

```bash
# Lijst modellen
curl http://localhost:5000/api/models

# Connect robot
curl -X POST http://localhost:5000/api/robot/connect \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.123.161"}'

# Activeer model
curl -X POST http://localhost:5000/api/models/go2_rl/activate

# Start control
curl -X POST http://localhost:5000/api/control/start

# Stop control
curl -X POST http://localhost:5000/api/control/stop
```

## Volgende Stappen

1. **Test API**: Test alle endpoints met curl of Postman
2. **Integreer met App**: Gebruik Programming functie of web interface
3. **Voeg UI toe**: Maak gebruiksvriendelijke interface
4. **Monitor**: Voeg logging en monitoring toe
5. **Secure**: Voeg authenticatie en HTTPS toe voor productie

