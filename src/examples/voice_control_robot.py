#!/usr/bin/env python3
"""
Voice Control Direct op Go2 Robot

Dit script is geoptimaliseerd om direct op de Go2 robot te draaien.
Gebruikt kleine Whisper modellen of Google Speech Recognition.

Gebruik: python src/examples/voice_control_robot.py --robot-ip 192.168.123.161
"""

import sys
import os
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.voice.voice_controller import Go2VoiceController

# Probeer officiële SDK te importeren (als beschikbaar op robot)
try:
    from src.unitree_go2.robot_official import Go2RobotOfficial
    HAS_OFFICIAL_SDK = True
except ImportError:
    try:
        from src.unitree_go2.robot import Go2Robot
        HAS_OFFICIAL_SDK = False
    except ImportError:
        print("⚠️  Geen robot SDK gevonden")
        HAS_OFFICIAL_SDK = None


class RobotVoiceController:
    """
    Voice controller geoptimaliseerd voor robot hardware
    """
    
    def __init__(
        self,
        robot_ip: str = "192.168.123.161",
        network_interface: str = None,
        whisper_model: str = "tiny",  # Klein model voor robot!
        use_cloud: bool = False,
        language: str = "nl-NL"
    ):
        """
        Initialiseer voice controller voor robot
        
        Args:
            robot_ip: Robot IP adres
            network_interface: Netwerk interface (voor officiële SDK)
            whisper_model: Whisper model (tiny of base aanbevolen)
            use_cloud: Gebruik cloud speech recognition (geen lokale Whisper)
            language: Taal voor spraakherkenning
        """
        self.robot_ip = robot_ip
        self.network_interface = network_interface
        
        # Initialiseer robot
        self.robot = None
        if HAS_OFFICIAL_SDK and network_interface:
            try:
                print(f"🔌 Verbinden met robot via officiële SDK...")
                self.robot = Go2RobotOfficial(
                    ip_address=robot_ip,
                    network_interface=network_interface
                )
                self.robot.connect()
                print("✓ Robot verbonden")
            except Exception as e:
                print(f"⚠️  Kon niet verbinden met officiële SDK: {e}")
                self.robot = None
        
        if not self.robot and HAS_OFFICIAL_SDK is False:
            try:
                print(f"🔌 Verbinden met robot via custom SDK...")
                self.robot = Go2Robot(ip_address=robot_ip)
                self.robot.connect()
                print("✓ Robot verbonden")
            except Exception as e:
                print(f"⚠️  Kon niet verbinden met robot: {e}")
                self.robot = None
        
        # Initialiseer voice controller
        print(f"🎤 Initialiseer voice controller...")
        if use_cloud:
            # Gebruik Google Speech Recognition (geen lokale Whisper)
            print("   Gebruik Google Speech Recognition (cloud)")
            self.voice_controller = Go2VoiceController(
                robot=self.robot,
                language=language,
                use_whisper=False,  # Geen lokale Whisper
                use_openai_api=False
            )
        else:
            # Gebruik lokale Whisper (klein model!)
            print(f"   Gebruik lokale Whisper (model: {whisper_model})")
            if whisper_model not in ["tiny", "base"]:
                print(f"⚠️  Waarschuwing: {whisper_model} kan te groot zijn voor robot!")
                print("   Overweeg 'tiny' of 'base' voor betere performance")
            
            self.voice_controller = Go2VoiceController(
                robot=self.robot,
                language=language,
                use_whisper=True,
                whisper_model=whisper_model,
                use_openai_api=False
            )
        
        print("✓ Voice controller geïnitialiseerd")
    
    def run(self):
        """Start voice control loop"""
        print("\n" + "=" * 70)
        print("  Voice Control op Go2 Robot")
        print("=" * 70)
        print("\nBeschikbare commando's:")
        print("  - 'sta op' - Laat robot rechtop staan")
        print("  - 'ga zitten' - Laat robot zitten")
        print("  - 'stop' - Stop alle beweging")
        print("  - 'help' - Toon help")
        print("\nDruk Ctrl+C om te stoppen\n")
        
        # Test microfoon
        print("🔊 Test microfoon...")
        self.voice_controller.speak("Microfoon test. Zeg iets.")
        test_text = self.voice_controller.listen_once(timeout=3.0)
        if test_text:
            print(f"✓ Test geslaagd: {test_text}")
        else:
            print("⚠️  Geen spraak gedetecteerd - check microfoon")
        
        # Start luisteren
        print("\n✓ Start luisteren...")
        self.voice_controller.speak("Ik luister. Zeg een commando.")
        
        self.voice_controller.start_listening()
        
        # Wacht op commando's
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Gestopt door gebruiker")
        
        self.voice_controller.stop_listening()
        
        # Cleanup
        if self.robot:
            try:
                self.robot.disconnect()
            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="Voice control direct op Go2 robot"
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
        default=None,
        help="Netwerk interface naam (voor officiële SDK, bijv. eth0)"
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default="tiny",
        choices=["tiny", "base", "small"],
        help="Whisper model grootte (default: tiny - aanbevolen voor robot)"
    )
    parser.add_argument(
        "--cloud",
        action="store_true",
        help="Gebruik Google Speech Recognition (geen lokale Whisper)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="nl-NL",
        help="Taal voor spraakherkenning (default: nl-NL)"
    )
    
    args = parser.parse_args()
    
    # Waarschuwing voor grote modellen
    if args.whisper_model in ["small", "medium", "large"] and not args.cloud:
        print("⚠️  Waarschuwing: Grote Whisper modellen kunnen te zwaar zijn voor robot!")
        print("   Overweeg --cloud voor cloud-based speech recognition")
        print("   Of gebruik --whisper-model tiny of base\n")
    
    try:
        controller = RobotVoiceController(
            robot_ip=args.robot_ip,
            network_interface=args.network_interface,
            whisper_model=args.whisper_model,
            use_cloud=args.cloud,
            language=args.language
        )
        
        controller.run()
        
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

