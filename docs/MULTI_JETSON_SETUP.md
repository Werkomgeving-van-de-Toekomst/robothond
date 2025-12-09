# Multi-Jetson Setup voor Go2 Robot

Complete guide voor het gebruik van meerdere Jetson AGX Orin devices parallel voor voice processing en andere AI taken.

## Overzicht

Het gebruik van meerdere Jetsons parallel biedt verschillende voordelen:
- **Load Balancing**: Verdeel workload over meerdere devices
- **Redundancy**: Fault tolerance - als één Jetson faalt, blijft systeem werken
- **Schaalbaarheid**: Meer capaciteit voor meerdere robots of complexere processing
- **Specialisatie**: Verschillende Jetsons voor verschillende taken
- **Lagere Latency**: Parallelle verwerking van meerdere commando's

## Architectuur Opties

### Optie 1: Load Balancing (Workload Verdeling)

```
┌─────────────┐
│   Go2 Robot │
└──────┬──────┘
       │
       │ Commando's
       ▼
┌─────────────────────────────────────┐
│      Load Balancer                  │
│      (API Gateway)                  │
└──────┬──────────────┬───────────────┘
       │              │
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│  Jetson 1   │  │  Jetson 2   │
│  Voice      │  │  Voice      │
│  Processing │  │  Processing │
└──────┬──────┘  └──────┬──────┘
       │                 │
       └────────┬────────┘
                │
                ▼
         ┌─────────────┐
         │  Go2 Robot │
         │  (Control) │
         └─────────────┘
```

**Voordelen**:
- Verdeel voice processing workload
- Snellere response tijd bij veel commando's
- Eén Jetson kan down zijn zonder systeem uitval

### Optie 2: Specialisatie (Verschillende Taken)

```
┌─────────────┐
│   Go2 Robot │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐    ┌─────────────┐
│  Jetson 1   │    │  Jetson 2   │
│  Voice      │    │  Vision/AI  │
│  Processing │    │  Processing │
└──────┬──────┘    └──────┬──────┘
       │                  │
       └────────┬─────────┘
                │
                ▼
         ┌─────────────┐
         │  Go2 Robot  │
         └─────────────┘
```

**Voordelen**:
- Specialisatie per Jetson
- Optimale performance per taak
- Complexere AI pipelines mogelijk

### Optie 3: Redundancy (Fault Tolerance)

```
┌─────────────┐
│   Go2 Robot │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐    ┌─────────────┐
│  Jetson 1   │    │  Jetson 2   │
│  (Primary)  │    │  (Backup)   │
│  Voice      │    │  Voice      │
└──────┬──────┘    └──────┬──────┘
       │                  │
       │  Failover        │
       └────────┬─────────┘
                │
                ▼
         ┌─────────────┐
         │  Go2 Robot  │
         └─────────────┘
```

**Voordelen**:
- Hoge beschikbaarheid
- Geen downtime bij hardware falen
- Automatische failover

## Voordelen van Multi-Jetson Setup

### 1. Performance Verbetering

**Single Jetson**:
- 1 voice commando tegelijk
- Latency: ~500-1000ms per commando
- Beperkt tot medium/large Whisper modellen

**Dual Jetson**:
- 2 voice commando's parallel
- Latency: ~250-500ms per commando (50% sneller)
- Kan beide large Whisper modellen draaien

### 2. Schaalbaarheid

| Scenario | Single Jetson | Dual Jetson |
|----------|---------------|-------------|
| 1 Robot | ✅ | ✅ |
| 2 Robots | ⚠️  (langzaam) | ✅ |
| 3+ Robots | ❌ | ✅ |
| Complexe AI | ⚠️  (beperkt) | ✅ |

### 3. Fault Tolerance

- **Single Jetson**: Als Jetson faalt → systeem down
- **Dual Jetson**: Als één Jetson faalt → systeem blijft werken (50% capaciteit)

### 4. Specialisatie

- **Jetson 1**: Voice processing (Whisper)
- **Jetson 2**: Computer vision (YOLO, object detection)
- **Jetson 3**: Path planning, navigation
- Etc.

## Implementatie

### Load Balancer Setup

#### Optie A: Simple Round-Robin Load Balancer

```python
#!/usr/bin/env python3
"""
Simple Load Balancer voor Multi-Jetson Voice Processing
"""

from flask import Flask, request, jsonify
import requests
import random
from typing import List

app = Flask(__name__)

# Lijst van Jetson servers
JETSON_SERVERS = [
    "http://192.168.1.100:8888",  # Jetson 1
    "http://192.168.1.101:8888",  # Jetson 2
]

current_server = 0

def get_next_server() -> str:
    """Round-robin server selectie"""
    global current_server
    server = JETSON_SERVERS[current_server]
    current_server = (current_server + 1) % len(JETSON_SERVERS)
    return server

def get_random_server() -> str:
    """Random server selectie"""
    return random.choice(JETSON_SERVERS)

def get_least_loaded_server() -> str:
    """Selecteer server met minste load"""
    best_server = None
    min_load = float('inf')
    
    for server in JETSON_SERVERS:
        try:
            response = requests.get(f"{server}/api/voice/status", timeout=1)
            if response.status_code == 200:
                data = response.json()
                # Gebruik command_count als load indicator
                load = data.get('command_count', 0)
                if load < min_load:
                    min_load = load
                    best_server = server
        except:
            continue
    
    return best_server or JETSON_SERVERS[0]

@app.route('/api/voice/listen', methods=['POST'])
def forward_voice_command():
    """Forward voice commando naar beschikbare Jetson"""
    # Kies server (round-robin, random, of least-loaded)
    server = get_least_loaded_server()
    
    try:
        # Forward request naar gekozen Jetson
        response = requests.post(
            f"{server}/api/voice/listen",
            json=request.get_json(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check voor alle Jetsons"""
    status = {}
    for server in JETSON_SERVERS:
        try:
            response = requests.get(f"{server}/health", timeout=1)
            status[server] = "online" if response.status_code == 200 else "offline"
        except:
            status[server] = "offline"
    
    return jsonify({
        "status": "ok",
        "jetsons": status
    })

if __name__ == '__main__':
    print("=" * 70)
    print("  Multi-Jetson Load Balancer")
    print("=" * 70)
    print(f"\nJetson servers: {JETSON_SERVERS}")
    print("\nStart load balancer op http://0.0.0.0:8889")
    app.run(host='0.0.0.0', port=8889, debug=True)
```

#### Optie B: Nginx Load Balancer

```nginx
# /etc/nginx/sites-available/jetson-loadbalancer
upstream jetson_voice {
    least_conn;  # Of: round-robin, ip_hash
    server 192.168.1.100:8888;
    server 192.168.1.101:8888;
}

server {
    listen 8889;
    
    location / {
        proxy_pass http://jetson_voice;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /health {
        # Health check endpoint
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### Client Configuratie

```python
# Client gebruikt load balancer IP in plaats van individuele Jetson
from src.voice.jetson_voice_client import JetsonVoiceClient

# Gebruik load balancer
client = JetsonVoiceClient(jetson_url="http://192.168.1.50:8889")  # Load balancer

# Commando's worden automatisch verdeeld over Jetsons
client.send_command("sta op")
```

## Configuratie

### Stap 1: Setup Jetson Servers

**Jetson 1**:
```bash
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --port 8888 \
    --whisper-model medium \
    --language nl-NL
```

**Jetson 2**:
```bash
python3 src/voice/jetson_voice_server.py \
    --robot-ip 192.168.123.161 \
    --network-interface eth0 \
    --port 8888 \
    --whisper-model medium \
    --language nl-NL
```

### Stap 2: Start Load Balancer

```bash
# Op aparte computer of één van de Jetsons
python3 src/voice/multi_jetson_loadbalancer.py
```

### Stap 3: Configureer Client

```bash
# Gebruik load balancer IP
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://192.168.1.50:8889 \
    --command "sta op"
```

## Use Cases

### Use Case 1: Meerdere Robots

```
Robot 1 ──┐
          ├──> Load Balancer ──> Jetson 1, Jetson 2
Robot 2 ──┘
```

**Voordelen**:
- Elke robot kan tegelijk commando's sturen
- Geen wachttijd tussen commando's
- Schaalbaar naar meer robots

### Use Case 2: Real-time + Batch Processing

```
Real-time Commando's ──> Jetson 1 (Voice)
Batch Analysis ────────> Jetson 2 (Vision/AI)
```

**Voordelen**:
- Real-time commando's hebben altijd prioriteit
- Batch processing blokkeert niet real-time
- Optimale resource gebruik

### Use Case 3: High Availability

```
Primary Commando's ──> Jetson 1 (Primary)
                       │
                       └──> Failover ──> Jetson 2 (Backup)
```

**Voordelen**:
- Geen downtime bij hardware falen
- Automatische failover
- Continuïteit van service

## Performance Vergelijking

### Single Jetson

| Metric | Waarde |
|--------|--------|
| Commando's/sec | ~1-2 |
| Latency | 500-1000ms |
| Max robots | 1-2 |
| Fault tolerance | Geen |

### Dual Jetson (Load Balanced)

| Metric | Waarde |
|--------|--------|
| Commando's/sec | ~2-4 |
| Latency | 250-500ms |
| Max robots | 2-4 |
| Fault tolerance | 50% capaciteit bij falen |

### Dual Jetson (Specialized)

| Metric | Waarde |
|--------|--------|
| Voice commando's/sec | ~2-4 |
| Vision processing | Real-time |
| Max robots | 1-2 (maar met vision) |
| Fault tolerance | Per taak |

## Monitoring

### Health Check Script

```python
#!/usr/bin/env python3
"""Monitor alle Jetson servers"""

import requests
import time
from typing import List

JETSON_SERVERS = [
    "http://192.168.1.100:8888",
    "http://192.168.1.101:8888",
]

def check_health(server: str) -> dict:
    """Check health van één Jetson"""
    try:
        response = requests.get(f"{server}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                "server": server,
                "status": "online",
                "robot_connected": data.get("robot_connected", False),
                "whisper_model": data.get("whisper_model", "unknown")
            }
    except:
        pass
    
    return {
        "server": server,
        "status": "offline"
    }

def monitor_all():
    """Monitor alle Jetsons"""
    while True:
        print("\n" + "=" * 70)
        print("  Jetson Health Status")
        print("=" * 70)
        
        for server in JETSON_SERVERS:
            health = check_health(server)
            status_icon = "✓" if health["status"] == "online" else "❌"
            print(f"{status_icon} {health['server']}: {health['status']}")
            if health["status"] == "online":
                print(f"   Robot: {'Verbonden' if health.get('robot_connected') else 'Niet verbonden'}")
                print(f"   Model: {health.get('whisper_model', 'unknown')}")
        
        time.sleep(5)

if __name__ == "__main__":
    monitor_all()
```

## Best Practices

### 1. Load Balancing Strategie

- **Round-Robin**: Gelijkmatige verdeling
- **Least Connections**: Verdeel naar minst belaste server
- **Random**: Voor testen
- **IP Hash**: Voor sessie persistentie

### 2. Health Checks

- Regelmatige health checks (elke 5 seconden)
- Automatische verwijdering van offline servers
- Automatische toevoeging wanneer server weer online komt

### 3. Failover Configuratie

- Primary/Backup setup voor kritieke toepassingen
- Automatische failover bij server falen
- Notificaties bij failover events

### 4. Monitoring

- Monitor CPU/GPU gebruik per Jetson
- Track latency per server
- Alert bij hoge load of falen

## Troubleshooting

### Probleem: Load balancer kan Jetsons niet bereiken

**Oplossing**:
```bash
# Test verbinding
ping 192.168.1.100  # Jetson 1
ping 192.168.1.101  # Jetson 2

# Test HTTP
curl http://192.168.1.100:8888/health
curl http://192.168.1.101:8888/health
```

### Probleem: Onbalans tussen Jetsons

**Oplossing**:
- Gebruik least-connections in plaats van round-robin
- Check individuele Jetson performance
- Overweeg specialisatie per Jetson

### Probleem: Hoge latency

**Oplossing**:
- Check netwerk verbinding tussen load balancer en Jetsons
- Monitor Jetson CPU/GPU gebruik
- Overweeg meer Jetsons toe te voegen

## Samenvatting

### Wanneer Multi-Jetson Gebruiken?

✅ **Gebruik meerdere Jetsons als**:
- Je meerdere robots hebt
- Je hoge beschikbaarheid nodig hebt
- Je verschillende AI taken parallel wilt draaien
- Je performance kritiek is

❌ **Gebruik single Jetson als**:
- Je maar één robot hebt
- Budget beperkt is
- Eenvoudige setup belangrijk is

### Quick Start

```bash
# 1. Start beide Jetson servers
# Jetson 1
python3 src/voice/jetson_voice_server.py --port 8888

# Jetson 2
python3 src/voice/jetson_voice_server.py --port 8888

# 2. Start load balancer
python3 src/voice/multi_jetson_loadbalancer.py

# 3. Gebruik load balancer
python3 src/voice/jetson_voice_client.py \
    --jetson-url http://loadbalancer:8889 \
    --command "sta op"
```

## Referenties

- [Jetson Voice Processing](./JETSON_VOICE_PROCESSING.md)
- [Jetson AGX Orin Verbinding](./JETSON_AGX_ORIN_VERBINDING.md)
- [Nederlandse Voice Control](./NEDERLANDSE_VOICE_CONTROL.md)

