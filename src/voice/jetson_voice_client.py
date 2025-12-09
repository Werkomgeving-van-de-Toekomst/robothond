#!/usr/bin/env python3
"""
Jetson Voice Client

Client die commando's naar Jetson Voice Server stuurt.
Kan gebruikt worden vanaf een andere computer of als wrapper.

Gebruik: python src/voice/jetson_voice_client.py --jetson-url http://192.168.1.100:8888
"""

import sys
import os
from pathlib import Path
import argparse
import requests
import json
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class JetsonVoiceClient:
    """
    Client voor Jetson Voice Server
    """
    
    def __init__(self, jetson_url: str = "http://localhost:8888"):
        """
        Initialiseer client
        
        Args:
            jetson_url: URL van Jetson Voice Server (bijv. http://192.168.1.100:8888)
        """
        self.jetson_url = jetson_url.rstrip('/')
        self.api_base = f"{self.jetson_url}/api"
    
    def health_check(self) -> bool:
        """Check of Jetson server bereikbaar is"""
        try:
            response = requests.get(f"{self.jetson_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def send_command(self, text: str) -> Optional[dict]:
        """
        Stuur tekst commando naar Jetson
        
        Args:
            text: Commando tekst
            
        Returns:
            Response dict of None bij fout
        """
        try:
            response = requests.post(
                f"{self.api_base}/voice/listen",
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Fout: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Fout bij verbinden met Jetson: {e}")
            return None
    
    def start_listening(self) -> bool:
        """Start continue luisteren op Jetson"""
        try:
            response = requests.post(f"{self.api_base}/voice/start", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def stop_listening(self) -> bool:
        """Stop luisteren op Jetson"""
        try:
            response = requests.post(f"{self.api_base}/voice/stop", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_status(self) -> Optional[dict]:
        """Get status van Jetson voice server"""
        try:
            response = requests.get(f"{self.api_base}/voice/status", timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def send_robot_command(self, command: str) -> bool:
        """
        Stuur direct commando naar robot via Jetson
        
        Args:
            command: Robot commando (stand, sit, stop)
        """
        try:
            response = requests.post(
                f"{self.api_base}/robot/command",
                json={"command": command},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_commands(self) -> Optional[list]:
        """Get lijst van beschikbare commando's"""
        try:
            response = requests.get(f"{self.api_base}/commands", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return data.get("commands", [])
        except:
            pass
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Jetson Voice Client"
    )
    parser.add_argument(
        "--jetson-url",
        type=str,
        default="http://localhost:8888",
        help="Jetson Voice Server URL"
    )
    parser.add_argument(
        "--command",
        type=str,
        default=None,
        help="Stuur direct commando (bijv. 'sta op')"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Toon status van Jetson server"
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start luisteren op Jetson"
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop luisteren op Jetson"
    )
    
    args = parser.parse_args()
    
    client = JetsonVoiceClient(jetson_url=args.jetson_url)
    
    # Health check
    print(f"🔍 Check verbinding met Jetson: {args.jetson_url}")
    if not client.health_check():
        print("❌ Jetson server niet bereikbaar!")
        print(f"   Check of server draait op {args.jetson_url}")
        return 1
    
    print("✓ Jetson server bereikbaar")
    
    # Status
    if args.status:
        status = client.get_status()
        if status:
            print("\n📊 Status:")
            print(f"   Luisteren: {'Actief' if status.get('is_listening') else 'Gestopt'}")
            print(f"   Robot verbonden: {'Ja' if status.get('robot_connected') else 'Nee'}")
            print(f"   Laatste commando: {status.get('last_command', 'Geen')}")
            print(f"   Commando teller: {status.get('command_count', 0)}")
    
    # Start luisteren
    if args.start:
        if client.start_listening():
            print("✓ Luisteren gestart op Jetson")
        else:
            print("❌ Kon luisteren niet starten")
    
    # Stop luisteren
    if args.stop:
        if client.stop_listening():
            print("✓ Luisteren gestopt op Jetson")
        else:
            print("❌ Kon luisteren niet stoppen")
    
    # Stuur commando
    if args.command:
        print(f"\n📤 Stuur commando: {args.command}")
        result = client.send_command(args.command)
        if result:
            print(f"✓ Commando verwerkt: {result.get('response', 'OK')}")
        else:
            print("❌ Commando niet verwerkt")
    
    # Interactive mode (als geen andere actie)
    if not any([args.status, args.start, args.stop, args.command]):
        print("\n📋 Beschikbare commando's:")
        commands = client.get_commands()
        if commands:
            for cmd in commands:
                print(f"   - {cmd}")
        
        print("\n💡 Gebruik:")
        print(f"   python {sys.argv[0]} --command 'sta op'")
        print(f"   python {sys.argv[0]} --status")
        print(f"   python {sys.argv[0]} --start")
        print(f"   python {sys.argv[0]} --stop")
    
    return 0


if __name__ == "__main__":
    exit(main())

