#!/usr/bin/env python3
"""
Diagnostiek script voor Unitree Go2 EDU

Controleert de verbinding en basis functionaliteit van de robot.
Gebruikt de officiële SDK.
"""

import sys
import os
import time
import socket
import platform
import subprocess

# Voeg parent directory toe aan path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.unitree_go2 import Go2Robot, Go2ConnectionError, Go2CommandError


def check_network_connectivity(ip_address):
    """Controleer of robot bereikbaar is via netwerk"""
    print(f"🔍 Controleren netwerkverbinding naar {ip_address}...")
    
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2000", ip_address],
            capture_output=True,
            timeout=3
        )
        if result.returncode == 0:
            print("✓ Netwerkverbinding OK")
            return True
        else:
            print("✗ Ping mislukt - robot niet bereikbaar")
            return False
    except Exception as e:
        print(f"✗ Netwerkfout: {e}")
        return False


def run_diagnostics(robot_ip="192.168.123.161", network_interface=None):
    """Voer volledige diagnostiek uit"""
    print("=" * 70)
    print("  Unitree Go2 EDU Diagnostiek")
    print("=" * 70)
    print(f"\nRobot IP: {robot_ip}\n")
    
    # 1. Netwerk check
    print("\n[1/5] Netwerkverbinding")
    print("-" * 70)
    if not check_network_connectivity(robot_ip):
        print("\n⚠️  Kan niet verbinden met robot via netwerk.")
        print("   Controleer:")
        print("   - Is de robot aan?")
        print("   - Is het IP adres correct?")
        print("   - Zijn beide apparaten op hetzelfde netwerk?")
        return False
    
    # 2. SDK verbinding
    print("\n[2/5] SDK Verbinding")
    print("-" * 70)
    
    if not network_interface:
        network_interface = "en0" if platform.system() == "Darwin" else "eth0"
    print(f"  Netwerk interface: {network_interface}")
    
    try:
        robot = Go2Robot(ip_address=robot_ip, network_interface=network_interface)
        robot.connect()
        print("✓ SDK verbinding succesvol")
    except Go2ConnectionError as e:
        print(f"✗ SDK verbinding mislukt: {e}")
        return False
    except Exception as e:
        print(f"✗ Onverwachte fout: {e}")
        return False
    
    # 3. Basis commando's
    print("\n[3/5] Basis Commando's")
    print("-" * 70)
    try:
        print("  Test stand commando...")
        result = robot.stand()
        print(f"  ✓ Stand: {result}")
        time.sleep(2)
        
        print("  Test sit commando...")
        result = robot.sit()
        print(f"  ✓ Sit: {result}")
        time.sleep(2)
        
        print("  Test stop commando...")
        result = robot.stop()
        print(f"  ✓ Stop: {result}")
        print("✓ Alle basis commando's werken")
    except Go2CommandError as e:
        print(f"✗ Commando fout: {e}")
        robot.disconnect()
        return False
    except Exception as e:
        print(f"✗ Onverwachte fout: {e}")
        robot.disconnect()
        return False
    
    # 4. Sensor data
    print("\n[4/5] Sensor Data")
    print("-" * 70)
    try:
        print("  Lezen robot status...")
        for i in range(3):
            state = robot.get_state()
            print(f"  ✓ Status {i+1}: {state}")
            time.sleep(0.5)
        print("✓ Sensor data lezen werkt")
    except Exception as e:
        print(f"✗ Sensor fout: {e}")
        robot.disconnect()
        return False
    
    # 5. Beweging test
    print("\n[5/5] Beweging Test")
    print("-" * 70)
    try:
        print("  ⚠️  Let op: Robot gaat nu bewegen!")
        print("  Druk Ctrl+C om te annuleren...")
        time.sleep(3)
        
        robot.stand()
        time.sleep(1)
        
        print("  Test beweging vooruit...")
        robot.move(vx=0.1, vy=0.0, vyaw=0.0)
        time.sleep(2)
        robot.stop()
        time.sleep(1)
        
        print("✓ Beweging werkt")
    except KeyboardInterrupt:
        print("\n  ⚠️  Beweging test geannuleerd door gebruiker")
    except Exception as e:
        print(f"✗ Beweging fout: {e}")
    finally:
        robot.stop()
        robot.sit()
        time.sleep(1)
    
    # Samenvatting
    print("\n" + "=" * 70)
    print("  Diagnostiek Voltooid")
    print("=" * 70)
    print("\n✓ Alle checks geslaagd!")
    print("\nJe robot is klaar voor gebruik.")
    print("Je kunt nu de test suite uitvoeren met: python run_tests.py")
    
    robot.disconnect()
    return True


def main():
    """Hoofdfunctie"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Voer diagnostiek uit op Unitree Go2 EDU robot'
    )
    parser.add_argument(
        '-i', '--ip',
        type=str,
        default="192.168.123.161",
        help='IP adres van de robot'
    )
    parser.add_argument(
        '--interface',
        type=str,
        default=None,
        help='Netwerk interface naam (bijv. en0, eth0)'
    )
    
    args = parser.parse_args()
    
    try:
        success = run_diagnostics(robot_ip=args.ip, network_interface=args.interface)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostiek geannuleerd door gebruiker")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Onverwachte fout: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

