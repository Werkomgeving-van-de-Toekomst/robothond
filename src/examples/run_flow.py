#!/usr/bin/env python3
"""
Run Flow voor Go2 Robot

Voer een flow uit (reeks van acties).
"""

import sys
import os
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.flow_executor import FlowExecutor, create_welcome_flow
from src.voice.voice_controller import Go2VoiceController


def main():
    parser = argparse.ArgumentParser(
        description="Voer een flow uit op de Go2 robot"
    )
    parser.add_argument(
        "--robot-ip",
        type=str,
        default="192.168.123.161",
        help="Robot IP adres"
    )
    parser.add_argument(
        "--flow",
        type=str,
        default="welcome",
        choices=["welcome", "custom"],
        help="Flow type (default: welcome)"
    )
    parser.add_argument(
        "--yaml",
        type=str,
        default=None,
        help="Pad naar YAML flow bestand"
    )
    parser.add_argument(
        "--distance",
        type=float,
        default=2.0,
        help="Afstand om te lopen voor welcome flow (meter)"
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Gebruik voice controller voor spraak"
    )
    parser.add_argument(
        "--whisper",
        action="store_true",
        help="Gebruik Whisper voor voice (als --voice gebruikt)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  Go2 Flow Executor")
    print("=" * 70)
    print(f"\nRobot IP: {args.robot_ip}")
    print(f"Flow: {args.flow}")
    
    try:
        # Connect robot
        robot = Go2Robot(ip_address=args.robot_ip)
        robot.connect()
        print("✓ Verbonden met robot")
        
        # Setup voice controller (optioneel)
        voice_controller = None
        if args.voice:
            try:
                voice_controller = Go2VoiceController(
                    robot=robot,
                    use_whisper=args.whisper,
                    whisper_model="base"
                )
                print("✓ Voice controller geïnitialiseerd")
            except Exception as e:
                print(f"⚠️  Kon voice controller niet initialiseren: {e}")
                print("   Flow gaat door zonder voice")
        
        # Maak flow executor
        executor = FlowExecutor(robot, voice_controller)
        
        # Setup callbacks
        def on_action_start(name):
            print(f"\n▶️  Start: {name}")
        
        def on_action_end(name):
            print(f"✓ Klaar: {name}")
        
        def on_flow_complete():
            print("\n🎉 Flow succesvol voltooid!")
        
        executor.on_action_start = on_action_start
        executor.on_action_end = on_action_end
        executor.on_flow_complete = on_flow_complete
        
        # Laad flow
        if args.yaml:
            print(f"\n📂 Laad flow uit: {args.yaml}")
            actions = executor.load_flow_from_yaml(args.yaml)
        elif args.flow == "welcome":
            print(f"\n📋 Maak welcome flow (afstand: {args.distance}m)")
            actions = create_welcome_flow(distance=args.distance)
        else:
            print("❌ Geen flow gespecificeerd")
            return 1
        
        print(f"\n📊 Flow bevat {len(actions)} acties:")
        for i, action in enumerate(actions, 1):
            name = action.get("name", action.get("type", "unknown"))
            print(f"  {i}. {name}")
        
        # Bevestiging
        print("\n⚠️  Druk Enter om flow te starten (Ctrl+C om te annuleren)...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n❌ Geannuleerd")
            return 0
        
        # Voer flow uit
        print("\n🚀 Start flow uitvoering...\n")
        success = executor.execute_flow(actions)
        
        if success:
            print("\n✓ Flow succesvol voltooid!")
            return 0
        else:
            print("\n❌ Flow mislukt")
            return 1
            
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

