#!/usr/bin/env python3
"""
API Server voor Unitree Go App Integratie

Maakt RL modellen beschikbaar via HTTP API die de Unitree Go app kan gebruiken.
"""

import sys
import os
from pathlib import Path
import json
import threading
import time
from typing import Optional, Dict, List, Any
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.rl_controller import Go2RLController, Go2ModelManager

app = Flask(__name__)
CORS(app)  # Enable CORS voor app toegang

# Globale state
robot: Optional[Go2Robot] = None
model_manager: Optional[Go2ModelManager] = None
current_controller: Optional[Go2RLController] = None
control_thread: Optional[threading.Thread] = None
is_running = False


def find_models(base_dir: str = "models") -> List[Dict[str, str]]:
    """Zoek alle beschikbare RL modellen"""
    models = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        return models
    
    # Zoek in subdirectories
    for model_dir in base_path.iterdir():
        if not model_dir.is_dir():
            continue
        
        # Zoek best_model.zip
        best_model = model_dir / "best_model" / "best_model.zip"
        final_model = model_dir / "final_model.zip"
        
        model_path = None
        if best_model.exists():
            model_path = str(best_model)
        elif final_model.exists():
            model_path = str(final_model)
        
        if model_path:
            # Haal configuratie op indien beschikbaar
            config_path = model_dir / "stair_config.json"
            config = {}
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            models.append({
                "name": model_dir.name,
                "path": model_path,
                "type": "stairs" if "stairs" in model_dir.name.lower() else "walking",
                "config": config
            })
    
    return models


@app.route('/api/models', methods=['GET'])
def list_models():
    """Lijst alle beschikbare modellen"""
    models = find_models()
    return jsonify({
        "status": "ok",
        "models": models,
        "count": len(models)
    })


@app.route('/api/models/<model_name>', methods=['GET'])
def get_model_info(model_name: str):
    """Haal informatie over specifiek model op"""
    models = find_models()
    model = next((m for m in models if m["name"] == model_name), None)
    
    if not model:
        return jsonify({"status": "error", "message": f"Model '{model_name}' niet gevonden"}), 404
    
    return jsonify({
        "status": "ok",
        "model": model
    })


@app.route('/api/robot/connect', methods=['POST'])
def connect_robot():
    """Connect met robot"""
    global robot, model_manager
    
    try:
        data = request.get_json() or {}
        ip_address = data.get("ip_address", "192.168.123.161")
        port = data.get("port", 8080)
        
        if robot is None:
            robot = Go2Robot(ip_address=ip_address, port=port)
        
        robot.connect()
        
        if model_manager is None:
            model_manager = Go2ModelManager(robot)
        
        return jsonify({
            "status": "ok",
            "message": "Verbonden met robot",
            "ip_address": ip_address
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/robot/disconnect', methods=['POST'])
def disconnect_robot():
    """Disconnect van robot"""
    global robot, model_manager, current_controller, is_running
    
    try:
        stop_control()
        
        if robot:
            robot.disconnect()
            robot = None
        
        model_manager = None
        current_controller = None
        
        return jsonify({
            "status": "ok",
            "message": "Verbinding verbroken"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/robot/status', methods=['GET'])
def robot_status():
    """Haal robot status op"""
    global robot, current_controller, is_running
    
    status = {
        "connected": robot is not None and robot.connected if robot else False,
        "current_model": None,
        "is_running": is_running,
        "loaded_models": []
    }
    
    if model_manager:
        status["loaded_models"] = model_manager.list_models()
        status["current_model"] = model_manager.current_model
    
    return jsonify({
        "status": "ok",
        "robot": status
    })


@app.route('/api/models/<model_name>/load', methods=['POST'])
def load_model(model_name: str):
    """Laad een model"""
    global model_manager, robot
    
    if not robot or not robot.connected:
        return jsonify({
            "status": "error",
            "message": "Niet verbonden met robot"
        }), 400
    
    if not model_manager:
        model_manager = Go2ModelManager(robot)
    
    try:
        models = find_models()
        model_info = next((m for m in models if m["name"] == model_name), None)
        
        if not model_info:
            return jsonify({
                "status": "error",
                "message": f"Model '{model_name}' niet gevonden"
            }), 404
        
        controller = model_manager.load_model(
            name=model_name,
            model_path=model_info["path"]
        )
        
        return jsonify({
            "status": "ok",
            "message": f"Model '{model_name}' geladen",
            "model": model_info
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/models/<model_name>/activate', methods=['POST'])
def activate_model(model_name: str):
    """Activeer een model (wissel ernaar)"""
    global model_manager, current_controller
    
    if not model_manager:
        return jsonify({
            "status": "error",
            "message": "Geen modellen geladen"
        }), 400
    
    try:
        controller = model_manager.switch_model(model_name)
        current_controller = controller
        
        return jsonify({
            "status": "ok",
            "message": f"Model '{model_name}' geactiveerd"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def control_loop():
    """Control loop die RL stappen uitvoert"""
    global current_controller, is_running
    
    while is_running:
        if current_controller:
            try:
                current_controller.step(deterministic=True)
            except Exception as e:
                print(f"Fout in control loop: {e}")
                break
        
        time.sleep(1.0 / 20.0)  # 20 Hz


@app.route('/api/control/start', methods=['POST'])
def start_control():
    """Start RL control"""
    global current_controller, control_thread, is_running
    
    if not current_controller:
        return jsonify({
            "status": "error",
            "message": "Geen model geactiveerd"
        }), 400
    
    if is_running:
        return jsonify({
            "status": "error",
            "message": "Control al actief"
        }), 400
    
    is_running = True
    control_thread = threading.Thread(target=control_loop, daemon=True)
    control_thread.start()
    
    return jsonify({
        "status": "ok",
        "message": "RL control gestart"
    })


@app.route('/api/control/stop', methods=['POST'])
def stop_control():
    """Stop RL control"""
    global is_running
    
    is_running = False
    
    return jsonify({
        "status": "ok",
        "message": "RL control gestopt"
    })


@app.route('/api/control/status', methods=['GET'])
def control_status():
    """Haal control status op"""
    return jsonify({
        "status": "ok",
        "is_running": is_running,
        "current_model": model_manager.current_model if model_manager else None
    })


@app.route('/api/robot/command', methods=['POST'])
def send_command():
    """Stuur direct commando naar robot (voor app integratie)"""
    global robot
    
    if not robot or not robot.connected:
        return jsonify({
            "status": "error",
            "message": "Niet verbonden met robot"
        }), 400
    
    try:
        data = request.get_json()
        command = data.get("command")
        
        if command == "stand":
            result = robot.stand()
        elif command == "sit":
            result = robot.sit()
        elif command == "stop":
            result = robot.stop()
        elif command == "move":
            vx = data.get("vx", 0.0)
            vy = data.get("vy", 0.0)
            vyaw = data.get("vyaw", 0.0)
            result = robot.move(vx, vy, vyaw)
        else:
            return jsonify({
                "status": "error",
                "message": f"Onbekend commando: {command}"
            }), 400
        
        return jsonify({
            "status": "ok",
            "result": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/voice/command', methods=['POST'])
def voice_command():
    """Ontvang voice commando en verwerk"""
    global current_controller, model_manager
    
    try:
        data = request.get_json()
        command_text = data.get("command", "").strip()
        
        if not command_text:
            return jsonify({
                "status": "error",
                "message": "Geen commando tekst"
            }), 400
        
        # Verwerk commando (simpele tekst matching)
        command_lower = command_text.lower()
        
        # Model selectie
        import re
        model_match = re.search(r"model\s+(\w+)|gebruik\s+model\s+(\w+)|selecteer\s+model\s+(\w+)", command_lower)
        if model_match:
            model_name = model_match.group(1) or model_match.group(2) or model_match.group(3)
            # Laad en activeer model
            if model_manager:
                try:
                    model_manager.load_model(model_name, f"models/{model_name}/best_model/best_model.zip")
                    model_manager.switch_model(model_name)
                    return jsonify({
                        "status": "ok",
                        "message": f"Model {model_name} geactiveerd",
                        "action": "model_selected",
                        "model": model_name
                    })
                except:
                    return jsonify({
                        "status": "error",
                        "message": f"Model {model_name} niet gevonden"
                    }), 404
        
        # Start control
        if "start" in command_lower and ("rl" in command_lower or "control" in command_lower):
            if not current_controller:
                return jsonify({
                    "status": "error",
                    "message": "Geen model geactiveerd"
                }), 400
            is_running = True
            return jsonify({
                "status": "ok",
                "message": "RL control gestart",
                "action": "control_started"
            })
        
        # Stop control
        if "stop" in command_lower:
            is_running = False
            if robot:
                robot.stop()
            return jsonify({
                "status": "ok",
                "message": "Robot gestopt",
                "action": "stopped"
            })
        
        # Stand
        if "sta op" in command_lower or "sta rechtop" in command_lower:
            if robot:
                robot.stand()
            return jsonify({
                "status": "ok",
                "message": "Robot staat rechtop",
                "action": "stand"
            })
        
        # Sit
        if "ga zitten" in command_lower or "zit" in command_lower:
            if robot:
                robot.sit()
            return jsonify({
                "status": "ok",
                "message": "Robot gaat zitten",
                "action": "sit"
            })
        
        # Onbekend commando
        return jsonify({
            "status": "error",
            "message": f"Commando niet herkend: {command_text}"
        }), 400
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/web/search', methods=['POST'])
def web_search():
    """Zoek op internet via API"""
    try:
        data = request.get_json()
        query = data.get("query", "")
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "Geen zoekterm opgegeven"
            }), 400
        
        from src.unitree_go2.web_search import WebSearcher
        searcher = WebSearcher()
        results = searcher.search(query, max_results=5)
        
        return jsonify({
            "status": "ok",
            "query": query,
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "Go2 RL Model API"
    })


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="API Server voor Unitree Go App integratie"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host om op te luisteren (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Poort om op te luisteren (default: 5000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  Go2 RL Model API Server")
    print("=" * 70)
    print(f"\nServer starten op http://{args.host}:{args.port}")
    print(f"API endpoints beschikbaar op /api/")
    print("\nBeschikbare endpoints:")
    print("  GET  /api/models              - Lijst alle modellen")
    print("  GET  /api/models/<name>       - Model informatie")
    print("  POST /api/models/<name>/load  - Laad model")
    print("  POST /api/models/<name>/activate - Activeer model")
    print("  POST /api/robot/connect       - Connect met robot")
    print("  POST /api/robot/disconnect    - Disconnect van robot")
    print("  GET  /api/robot/status        - Robot status")
    print("  POST /api/control/start       - Start RL control")
    print("  POST /api/control/stop        - Stop RL control")
    print("  GET  /api/control/status      - Control status")
    print("  POST /api/robot/command       - Stuur commando")
    print("\nDruk Ctrl+C om te stoppen\n")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Server gestopt")
        if robot:
            robot.disconnect()


if __name__ == "__main__":
    main()

