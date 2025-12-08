#!/usr/bin/env python3
"""
Test of je Go2 EDU variant hebt

Test of de robot SDK toegang heeft (EDU variant vereist).
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.unitree_go2 import Go2Robot, Go2ConnectionError


def test_edu_variant(ip_address="192.168.123.161"):
    """Test of robot EDU variant is"""
    
    print("=" * 70)
    print("  Go2 EDU Variant Test")
    print("=" * 70)
    print(f"\nTest verbinding met robot op {ip_address}...")
    
    try:
        robot = Go2Robot(ip_address=ip_address)
        robot.connect()
        print("✓ Verbinding succesvol!")
        
        # Test basis commando
        print("\nTest basis commando (stand)...")
        try:
            result = robot.stand()
            print("✓ Stand commando werkt!")
            print(f"  Resultaat: {result}")
            
            # Wacht even
            import time
            time.sleep(1.0)
            
            # Test sensor data
            print("\nTest sensor data ophalen...")
            state = robot.get_state()
            print("✓ Sensor data toegankelijk!")
            
            if 'battery_level' in state:
                print(f"  Batterij: {state['battery_level']}%")
            if 'base_position' in state:
                pos = state['base_position']
                print(f"  Positie: x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f}")
            
            # Test beweging commando
            print("\nTest beweging commando...")
            robot.move(vx=0.0, vy=0.0, vyaw=0.0)  # Stop commando
            print("✓ Beweging commando werkt!")
            
            robot.stop()
            
            print("\n" + "=" * 70)
            print("  ✅ JE HEBT WAARSCHIJNLIJK DE EDU VARIANT!")
            print("=" * 70)
            print("\nAlle SDK functies werken correct.")
            print("Je kunt de volledige SDK gebruiken voor ontwikkeling.")
            
            robot.disconnect()
            return True
            
        except Exception as e:
            print(f"⚠️  Commando test mislukt: {e}")
            print("\nDit kan betekenen:")
            print("  - Je hebt de standaard variant (geen SDK toegang)")
            print("  - Ontwikkelaarsmodus is niet ingeschakeld")
            print("  - Robot firmware is niet up-to-date")
            print("  - Robot accepteert geen commando's op dit moment")
            
            try:
                robot.disconnect()
            except:
                pass
            return False
            
    except Go2ConnectionError as e:
        print(f"❌ Verbindingsfout: {e}")
        print("\nMogelijke oorzaken:")
        print("  - Robot is niet aan")
        print("  - Verkeerd IP adres")
        print("  - Netwerkproblemen")
        print("  - Firewall blokkeert verbinding")
        print("\nProbeer:")
        print("  1. Check of robot aan is")
        print("  2. Ping robot: ping 192.168.123.161")
        print("  3. Check netwerk verbinding")
        return False
    except Exception as e:
        print(f"❌ Onverwachte fout: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test of je Go2 EDU variant hebt"
    )
    parser.add_argument(
        "-i", "--ip",
        type=str,
        default="192.168.123.161",
        help="Robot IP adres (default: 192.168.123.161)"
    )
    
    args = parser.parse_args()
    
    success = test_edu_variant(args.ip)
    
    if success:
        print("\n✓ Test voltooid - EDU variant gedetecteerd")
        return 0
    else:
        print("\n⚠️  Test voltooid - EDU variant niet bevestigd")
        print("\nAls je zeker weet dat je EDU variant hebt:")
        print("  - Check ontwikkelaarsmodus in Unitree Go app")
        print("  - Update robot firmware")
        print("  - Contact Unitree support")
        return 1


if __name__ == "__main__":
    exit(main())

