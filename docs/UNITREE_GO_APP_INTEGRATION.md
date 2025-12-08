# Unitree Go App Integratie

Deze guide beschrijft hoe je de officiële [Unitree Go app](https://apps.apple.com/us/app/unitree-go-embodied-ai/id1579283821) kunt gebruiken om RL modellen te selecteren.

## Overzicht

De Unitree Go app heeft een **"Programming"** functie die we kunnen gebruiken om HTTP requests te maken naar onze API server. Hiermee kun je modellen selecteren en activeren vanuit de app.

## Setup

### Stap 1: Installeer Dependencies

```bash
conda activate pybullet  # Of je normale venv
pip install flask flask-cors
```

### Stap 2: Start API Server

```bash
# Start server op je computer (moet opzelfde netwerk als telefoon)
python src/controller_app/model_api_server.py --host 0.0.0.0 --port 5000
```

### Stap 3: Vind je Computer IP Adres

```bash
# Op macOS
ifconfig | grep "inet " | grep -v 127.0.0.1

# Of
ipconfig getifaddr en0  # WiFi
ipconfig getifaddr en1  # Ethernet
```

Noteer dit IP adres - je hebt het nodig in de app.

### Stap 4: Test API Server

Open in browser op je telefoon (of computer):
```
http://<jouw-ip>:5000/api/health
```

Je zou moeten zien: `{"status": "ok", "service": "Go2 RL Model API"}`

## Gebruik met Unitree Go App

### Methode 1: Via Programming Functie

De Unitree Go app heeft een "Programming" functie die HTTP requests kan maken:

1. **Open Unitree Go app** op je iPhone/iPad
2. **Ga naar "Features"** → **"Programming"** (of "Creative Workshop")
3. **Maak nieuw programma**

#### Programma: Model Selecteren

Maak een programma met deze stappen:

**Stap 1: Lijst Modellen**
- Gebruik "HTTP Request" blok
- Method: `GET`
- URL: `http://<jouw-ip>:5000/api/models`
- Sla resultaat op in variabele `models`

**Stap 2: Toon Modellen**
- Gebruik "Show Message" of "Display" blok
- Toon lijst van modellen uit `models`

**Stap 3: Gebruiker Selecteert**
- Gebruik "Input" of "Button" blok
- Laat gebruiker model naam invoeren/selecteren

**Stap 4: Laad Model**
- HTTP Request: `POST`
- URL: `http://<jouw-ip>:5000/api/models/<model_naam>/load`

**Stap 5: Activeer Model**
- HTTP Request: `POST`
- URL: `http://<jouw-ip>:5000/api/models/<model_naam>/activate`

**Stap 6: Start Control**
- HTTP Request: `POST`
- URL: `http://<jouw-ip>:5000/api/control/start`

### Methode 2: Via Web Interface (Eenvoudiger)

1. **Open web browser** op je telefoon (Safari op iPhone)
2. **Ga naar**: Open `src/controller_app/simple_web_ui.html` in browser
3. **Pas IP adres aan**: Edit het HTML bestand en verander `API_BASE` naar jouw server IP
4. **Of gebruik direct**: `http://<jouw-ip>:5000` (als je de HTML serveert)

De web interface heeft:
- ✅ Model lijst met visuele kaarten
- ✅ Eén klik activatie
- ✅ Start/Stop knoppen
- ✅ Robot verbinding status
- ✅ Mobile-friendly design

### Methode 3: Via iOS Shortcuts (Aanbevolen)

Maak iOS Shortcuts die de API aanroepen:

1. **Open Shortcuts app** op iPhone
2. **Maak nieuwe shortcut**: "Selecteer RL Model"
3. **Voeg acties toe**:

```
1. "Ask for Input" → Model naam
2. "Get Contents of URL"
   - URL: http://<jouw-ip>:5000/api/models/{Input}/activate
   - Method: POST
3. "Get Contents of URL"
   - URL: http://<jouw-ip>:5000/api/control/start
   - Method: POST
4. "Show Notification" → "Model geactiveerd!"
```

4. **Voeg toe aan Home Screen** voor snelle toegang

## API Endpoints voor App

### Model Beheer

```
GET  /api/models                    - Lijst alle modellen
GET  /api/models/<name>            - Model informatie
POST /api/models/<name>/load       - Laad model
POST /api/models/<name>/activate   - Activeer model
```

### Robot Control

```
POST /api/robot/connect            - Connect met robot
POST /api/robot/disconnect         - Disconnect
GET  /api/robot/status             - Robot status
POST /api/control/start            - Start RL control
POST /api/control/stop             - Stop RL control
GET  /api/control/status           - Control status
```

### Direct Commando's

```
POST /api/robot/command            - Stuur commando (stand, sit, move, stop)
```

## Voorbeeld: Programma in Unitree Go App

Hier is een voorbeeld van hoe je een programma kunt maken in de Unitree Go app:

### Programma: "RL Model Selector"

**Blok 1: Vraag Model Naam**
- Type: Input
- Prompt: "Welk model wil je gebruiken?"
- Options: ["go2_rl", "go2_stairs"]
- Sla op in: `model_name`

**Blok 2: Connect Robot**
- Type: HTTP Request
- Method: POST
- URL: `http://<jouw-ip>:5000/api/robot/connect`
- Body: `{"ip_address": "192.168.123.161"}`

**Blok 3: Laad Model**
- Type: HTTP Request
- Method: POST
- URL: `http://<jouw-ip>:5000/api/models/{model_name}/load`

**Blok 4: Activeer Model**
- Type: HTTP Request
- Method: POST
- URL: `http://<jouw-ip>:5000/api/models/{model_name}/activate`

**Blok 5: Start Control**
- Type: HTTP Request
- Method: POST
- URL: `http://<jouw-ip>:5000/api/control/start`

**Blok 6: Toon Bevestiging**
- Type: Show Message
- Message: "Model {model_name} geactiveerd en gestart!"

## Troubleshooting

### App kan server niet bereiken

1. **Check netwerk**: Zorg dat telefoon en computer opzelfde WiFi zitten
2. **Check firewall**: Zorg dat poort 5000 open is
3. **Check IP adres**: Verifieer dat je het juiste IP gebruikt
4. **Test in browser**: Open `http://<ip>:5000/api/health` in Safari

### HTTP Requests werken niet in App

- De Unitree Go app Programming functie heeft mogelijk beperkte HTTP support
- Gebruik in dat geval de **Web Interface** of **iOS Shortcuts** methode

### Model laadt niet

- Check of model pad bestaat
- Verifieer dat robot verbonden is
- Check server logs voor errors

## Veiligheid

⚠️ **BELANGRIJK**:

1. **Lokaal netwerk**: Server draait alleen op lokaal netwerk
2. **Firewall**: Beperk toegang tot poort 5000
3. **HTTPS**: Overweeg HTTPS voor productie (vereist certificaat)
4. **Authentication**: Voeg authenticatie toe voor productie gebruik

## Snelle Start

```bash
# 1. Start server
python src/controller_app/model_api_server.py --host 0.0.0.0 --port 5000

# 2. Vind IP
ipconfig getifaddr en0  # macOS WiFi

# 3. Test in browser (op telefoon)
http://<jouw-ip>:5000/api/models

# 4. Gebruik web UI of app Programming functie
```

## Voorbeelden

### cURL Testen (op computer)

```bash
# Lijst modellen
curl http://localhost:5000/api/models

# Activeer model
curl -X POST http://localhost:5000/api/models/go2_rl/activate

# Start control
curl -X POST http://localhost:5000/api/control/start
```

### Python Test Script

```python
import requests

API_BASE = "http://192.168.1.100:5000/api"  # Jouw IP

# Lijst modellen
models = requests.get(f"{API_BASE}/models").json()
print(f"Modellen: {[m['name'] for m in models['models']]}")

# Activeer model
requests.post(f"{API_BASE}/models/go2_rl/activate")
requests.post(f"{API_BASE}/control/start")
```

## Volgende Stappen

1. **Test API**: Test alle endpoints eerst met curl/browser
2. **Setup App**: Maak programma in Unitree Go app
3. **Test Integratie**: Test model selectie vanuit app
4. **Voeg UI toe**: Gebruik web interface voor betere UX
5. **Secure**: Voeg authenticatie toe voor productie

