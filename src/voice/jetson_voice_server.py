#!/usr/bin/env python3
"""
Jetson Voice Server voor Go2 Robot

Deze server draait op de Jetson AGX Orin en verzorgt:
- Spraakherkenning (Whisper)
- Commando interpretatie
- Robot controle via netwerk
- Text-to-speech feedback

Gebruik: python src/voice/jetson_voice_server.py --robot-ip 192.168.123.161 --port 8888
"""

import sys
import os
from pathlib import Path
import argparse
import json
import threading
import time
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.voice.voice_controller import Go2VoiceController
from src.unitree_go2.robot_official import Go2RobotOfficial
from src.unitree_go2.web_search import WebSearcher


class JetsonVoiceServer:
    """
    Voice server die op Jetson draait en spraakverwerking verzorgt
    """
    
    def __init__(
        self,
        robot_ip: str = "192.168.123.161",
        network_interface: str = "eth0",
        port: int = 8888,
        whisper_model: str = "base",
        language: str = "nl-NL",
        use_robot: bool = True
    ):
        """
        Initialiseer Jetson voice server
        
        Args:
            robot_ip: IP adres van Go2 robot
            network_interface: Netwerk interface naam (bijv. eth0)
            port: HTTP server poort
            whisper_model: Whisper model grootte (tiny, base, small, medium, large)
            language: Taal voor spraakherkenning
            use_robot: Of robot direct verbonden moet worden
        """
        self.robot_ip = robot_ip
        self.network_interface = network_interface
        self.port = port
        self.whisper_model = whisper_model
        self.language = language
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)  # Sta cross-origin requests toe
        
        # Setup routes
        self.setup_routes()
        
        # Robot verbinding
        self.robot = None
        if use_robot:
            try:
                print(f"🔌 Verbinden met robot op {robot_ip} via {network_interface}...")
                self.robot = Go2RobotOfficial(
                    ip_address=robot_ip,
                    network_interface=network_interface
                )
                self.robot.connect()
                print("✓ Robot verbonden")
            except Exception as e:
                print(f"⚠️  Kon niet verbinden met robot: {e}")
                print("   Server draait zonder robot verbinding")
                self.robot = None
        
        # Voice controller
        print(f"🎤 Initialiseer voice controller (Whisper model: {whisper_model})...")
        try:
            self.voice_controller = Go2VoiceController(
                robot=self.robot,
                language=language,
                use_whisper=True,  # Altijd Whisper gebruiken op Jetson
                whisper_model=whisper_model,
                web_searcher=WebSearcher()  # Voor internet zoeken
            )
            print("✓ Voice controller geïnitialiseerd")
        except Exception as e:
            print(f"❌ Fout bij initialiseren voice controller: {e}")
            raise
        
        # State
        self.is_listening = False
        self.last_command = None
        self.command_history = []
        
        print(f"\n✓ Jetson Voice Server klaar!")
        print(f"  Robot: {'Verbonden' if self.robot else 'Niet verbonden'}")
        print(f"  Whisper model: {whisper_model}")
        print(f"  Taal: {language}")
        print(f"  Server poort: {port}")
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "ok",
                "robot_connected": self.robot is not None,
                "whisper_model": self.whisper_model,
                "language": self.language
            })
        
        @self.app.route('/api/voice/listen', methods=['POST'])
        def listen():
            """
            Luister naar spraak en verwerk commando
            
            Accepteert audio data (WAV format) of tekst commando
            """
            try:
                data = request.get_json()
                
                # Als tekst commando
                if 'text' in data:
                    text = data['text']
                    print(f"📝 Ontvangen tekst commando: {text}")
                    result = self.voice_controller.process_command(text)
                    return jsonify({
                        "status": "ok",
                        "recognized": text,
                        "processed": result,
                        "response": self.get_response_text(text)
                    })
                
                # Als audio data (base64 encoded WAV)
                elif 'audio' in data:
                    # TODO: Implementeer audio decoding en processing
                    return jsonify({
                        "status": "error",
                        "message": "Audio processing nog niet geïmplementeerd"
                    }), 501
                
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Geen tekst of audio data"
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/voice/start', methods=['POST'])
        def start_listening():
            """Start continue luisteren"""
            if self.is_listening:
                return jsonify({
                    "status": "error",
                    "message": "Luisteren al actief"
                }), 400
            
            self.is_listening = True
            
            def listen_loop():
                while self.is_listening:
                    text = self.voice_controller.listen_once(timeout=3.0)
                    if text:
                        self.voice_controller.process_command(text)
                        self.last_command = text
                        self.command_history.append({
                            "text": text,
                            "timestamp": time.time()
                        })
            
            thread = threading.Thread(target=listen_loop, daemon=True)
            thread.start()
            
            return jsonify({
                "status": "ok",
                "message": "Luisteren gestart"
            })
        
        @self.app.route('/api/voice/stop', methods=['POST'])
        def stop_listening():
            """Stop met luisteren"""
            self.is_listening = False
            self.voice_controller.stop_listening()
            return jsonify({
                "status": "ok",
                "message": "Luisteren gestopt"
            })
        
        @self.app.route('/api/voice/status', methods=['GET'])
        def status():
            """Get voice server status"""
            return jsonify({
                "status": "ok",
                "is_listening": self.is_listening,
                "robot_connected": self.robot is not None,
                "last_command": self.last_command,
                "command_count": len(self.command_history)
            })
        
        @self.app.route('/api/robot/command', methods=['POST'])
        def robot_command():
            """Stuur direct commando naar robot"""
            if not self.robot:
                return jsonify({
                    "status": "error",
                    "message": "Robot niet verbonden"
                }), 400
            
            try:
                data = request.get_json()
                command = data.get('command', '').lower()
                
                if command == 'stand':
                    self.robot.stand()
                elif command == 'sit':
                    self.robot.sit()
                elif command == 'stop':
                    self.robot.stop()
                else:
                    return jsonify({
                        "status": "error",
                        "message": f"Onbekend commando: {command}"
                    }), 400
                
                return jsonify({
                    "status": "ok",
                    "message": f"Commando '{command}' uitgevoerd"
                })
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/commands', methods=['GET'])
        def get_commands():
            """Get beschikbare commando's"""
            return jsonify({
                "status": "ok",
                "commands": [
                    "sta op",
                    "ga zitten",
                    "stop",
                    "model [naam]",
                    "start",
                    "zoek [term]",
                    "vind [term]"
                ]
            })
    
    def get_response_text(self, command: str) -> str:
        """Genereer response tekst voor commando"""
        command_lower = command.lower()
        
        if "sta op" in command_lower or "sta rechtop" in command_lower:
            return "Robot staat rechtop"
        elif "ga zitten" in command_lower or "zit" in command_lower:
            return "Robot gaat zitten"
        elif "stop" in command_lower:
            return "Robot gestopt"
        elif "zoek" in command_lower or "vind" in command_lower:
            return "Zoekopdracht uitgevoerd"
        else:
            return "Commando verwerkt"
    
    def run(self, host: str = "0.0.0.0", debug: bool = False):
        """Start Flask server"""
        print(f"\n🚀 Start Jetson Voice Server op {host}:{self.port}")
        print(f"   API endpoints beschikbaar op http://{host}:{self.port}/api")
        print(f"\n   Beschikbare endpoints:")
        print(f"   - GET  /health")
        print(f"   - POST /api/voice/listen")
        print(f"   - POST /api/voice/start")
        print(f"   - POST /api/voice/stop")
        print(f"   - GET  /api/voice/status")
        print(f"   - POST /api/robot/command")
        print(f"   - GET  /api/commands")
        print(f"\n   Druk Ctrl+C om te stoppen\n")
        
        self.app.run(host=host, port=self.port, debug=debug, threaded=True)
    
    def shutdown(self):
        """Cleanup bij afsluiten"""
        if self.is_listening:
            self.voice_controller.stop_listening()
        if self.robot:
            try:
                self.robot.disconnect()
            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="Jetson Voice Server voor Go2 Robot"
    )
    parser.add_argument(
        "--robot-ip",
        type=str,
        default="192.168.123.161",
        help="Robot IP adres"
    )
    parser.add_argument(
        "--network-interface",
        type=str,
        default="eth0",
        help="Netwerk interface naam (bijv. eth0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8888,
        help="HTTP server poort"
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model grootte (default: base)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="nl-NL",
        help="Taal voor spraakherkenning (default: nl-NL)"
    )
    parser.add_argument(
        "--no-robot",
        action="store_true",
        help="Start zonder robot verbinding (alleen voice processing)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  Jetson Voice Server voor Go2 Robot")
    print("=" * 70)
    
    try:
        server = JetsonVoiceServer(
            robot_ip=args.robot_ip,
            network_interface=args.network_interface,
            port=args.port,
            whisper_model=args.whisper_model,
            language=args.language,
            use_robot=not args.no_robot
        )
        
        server.run(host=args.host, debug=args.debug)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Gestopt door gebruiker")
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if 'server' in locals():
            server.shutdown()
    
    return 0


if __name__ == "__main__":
    exit(main())

