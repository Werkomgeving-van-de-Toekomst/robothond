#!/usr/bin/env python3
"""
Voice Control voor Go2 Robot

Spreek commando's uit om de robot te besturen.
"""

import sys
import os
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.voice.voice_controller import Go2VoiceController
from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.web_search import WebSearcher


def main():
    parser = argparse.ArgumentParser(
        description="Voice control voor Go2 robot"
    )
    parser.add_argument(
        "--api",
        type=str,
        default=None,
        help="API server URL (bijv. http://localhost:5000/api)"
    )
    parser.add_argument(
        "--robot-ip",
        type=str,
        default="192.168.123.161",
        help="Robot IP adres (alleen als --api niet gebruikt)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="nl-NL",
        help="Taal voor spraakherkenning (default: nl-NL)"
    )
    parser.add_argument(
        "--whisper",
        action="store_true",
        help="Gebruik lokale OpenAI Whisper (open source)"
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model grootte (default: base)"
    )
    parser.add_argument(
        "--openai-api",
        action="store_true",
        help="Gebruik OpenAI API (vereist API key)"
    )
    parser.add_argument(
        "--openai-key",
        type=str,
        default=None,
        help="OpenAI API key (of gebruik OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  Voice Control voor Go2 Robot")
    print("=" * 70)
    print(f"\nTaal: {args.language}")
    print(f"Whisper (lokaal): {args.whisper}")
    if args.whisper:
        print(f"  Model: {args.whisper_model}")
    print(f"OpenAI API: {args.openai_api}")
    
    if args.api:
        print(f"API Server: {args.api}")
    else:
        print(f"Directe robot verbinding: {args.robot_ip}")
    
    print("\nBeschikbare commando's:")
    print("  - 'sta op' - Laat robot rechtop staan")
    print("  - 'ga zitten' - Laat robot zitten")
    print("  - 'stop' - Stop alle beweging")
    print("  - 'model [naam]' - Selecteer RL model")
    print("  - 'start' - Start RL control")
    print("  - 'zoek [term]' - Zoek op internet")
    print("  - 'vind [term]' - Zoek op internet")
    print("  - 'help' - Toon help")
    print("\nDruk Ctrl+C om te stoppen\n")
    
    # Setup robot (als geen API)
    robot = None
    if not args.api:
        try:
            robot = Go2Robot(ip_address=args.robot_ip)
            robot.connect()
            print("✓ Verbonden met robot")
        except Exception as e:
            print(f"⚠️  Kon niet verbinden met robot: {e}")
            print("   Gebruik --api voor API server mode")
            robot = None
    
        # Setup web searcher (voor internet zoeken)
        web_searcher = None
        if args.display_url or True:  # Altijd beschikbaar maken
            try:
                web_searcher = WebSearcher()
                print("✓ Web searcher geïnitialiseerd")
            except Exception as e:
                print(f"⚠️  Kon web searcher niet initialiseren: {e}")
        
        # Setup voice controller
        openai_key = args.openai_key or os.getenv("OPENAI_API_KEY")
        
        try:
            controller = Go2VoiceController(
                robot=robot,
                api_base=args.api,
                language=args.language,
                use_whisper=args.whisper,
                whisper_model=args.whisper_model,
                use_openai_api=args.openai_api,
                openai_api_key=openai_key,
                web_searcher=web_searcher,
                display_api_url=args.display_url
            )
        
        print("✓ Voice controller geïnitialiseerd")
        
        # Test microfoon
        print("\n🔊 Test microfoon...")
        controller.speak("Microfoon test. Zeg iets.")
        test_text = controller.listen_once(timeout=3.0)
        if test_text:
            print(f"✓ Test geslaagd: {test_text}")
        else:
            print("⚠️  Geen spraak gedetecteerd - check microfoon")
        
        # Start luisteren
        print("\n✓ Start luisteren...")
        controller.speak("Ik luister. Zeg een commando.")
        
        controller.start_listening()
        
        # Wacht op commando's
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Gestopt door gebruiker")
        
        controller.stop_listening()
        
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if robot:
            robot.disconnect()
    
    return 0


if __name__ == "__main__":
    exit(main())

