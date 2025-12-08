#!/usr/bin/env python3
"""
Search and Display voor Go2 Robot

Zoek iets op internet en toon resultaten op gekoppelde PC.
"""

import sys
import os
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.flow_executor import FlowExecutor
from src.unitree_go2.web_search import WebSearcher
from src.voice.voice_controller import Go2VoiceController


def main():
    parser = argparse.ArgumentParser(
        description="Zoek op internet en toon resultaten op display"
    )
    parser.add_argument(
        "--robot-ip",
        type=str,
        default="192.168.123.161",
        help="Robot IP adres"
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Zoekterm"
    )
    parser.add_argument(
        "--display-url",
        type=str,
        default="http://localhost:5001/api",
        help="Display server API URL"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum aantal zoekresultaten"
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Gebruik voice controller voor spraak"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Toon niet op display (alleen print)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  Go2 Internet Zoeken en Display")
    print("=" * 70)
    print(f"\nZoekterm: {args.query}")
    print(f"Display URL: {args.display_url}")
    
    try:
        # Connect robot
        robot = Go2Robot(ip_address=args.robot_ip)
        robot.connect()
        print("✓ Verbonden met robot")
        
        # Setup web searcher
        searcher = WebSearcher(search_engine="duckduckgo")
        print("✓ Web searcher geïnitialiseerd")
        
        # Setup voice controller (optioneel)
        voice_controller = None
        if args.voice:
            try:
                voice_controller = Go2VoiceController(
                    robot=robot,
                    use_whisper=False
                )
                print("✓ Voice controller geïnitialiseerd")
            except Exception as e:
                print(f"⚠️  Kon voice controller niet initialiseren: {e}")
        
        # Maak flow executor
        display_url = None if args.no_display else args.display_url
        executor = FlowExecutor(
            robot=robot,
            voice_controller=voice_controller,
            web_searcher=searcher,
            display_api_url=display_url
        )
        
        # Zoek op internet
        print(f"\n🔍 Zoeken op internet: {args.query}")
        results = searcher.search(args.query, args.max_results)
        
        print(f"\n✓ {len(results)} resultaten gevonden:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   {result['snippet'][:150]}...")
        
        # Toon op display
        if not args.no_display:
            print(f"\n📺 Verstuur naar display server...")
            try:
                import requests
                response = requests.post(
                    f"{args.display_url}/display/search",
                    json={
                        "query": args.query,
                        "results": results
                    },
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✓ Resultaten getoond op display")
                    print(f"  Open in browser: {args.display_url.replace('/api', '')}")
                else:
                    print(f"⚠️  Display server fout: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Kon niet verbinden met display server: {e}")
                print(f"   Start display server met: python src/controller_app/display_server.py")
        
        # Spreek resultaten uit (optioneel)
        if args.voice and voice_controller:
            summary = searcher.search_and_summarize(args.query, max_results=3)
            print(f"\n🔊 Spreek resultaten uit...")
            voice_controller.speak(summary)
        
        print("\n✓ Klaar!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Gestopt door gebruiker")
        return 0
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if 'robot' in locals():
            robot.disconnect()


if __name__ == "__main__":
    exit(main())

