"""
Sensor data lezen voorbeeld voor Unitree Go2 EDU

Dit script demonstreert hoe je sensor data van de robot kunt lezen.
Gebruikt de officiële SDK.
"""

import sys
import os
import time
import argparse
import platform

# Voeg parent directory toe aan path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.unitree_go2 import Go2Robot


def main():
    """Sensor data lezen demo"""
    
    parser = argparse.ArgumentParser(description='Sensor data lezen demo voor Go2')
    parser.add_argument('-i', '--ip', default="192.168.123.161", help='Robot IP adres')
    parser.add_argument('--interface', default=None, help='Netwerk interface (bijv. en0, eth0)')
    args = parser.parse_args()
    
    robot_ip = args.ip
    network_interface = args.interface or ("en0" if platform.system() == "Darwin" else "eth0")
    
    print(f"Verbinden met robot op {robot_ip} via {network_interface}...")
    
    try:
        # Maak verbinding met robot
        with Go2Robot(ip_address=robot_ip, network_interface=network_interface) as robot:
            print("Verbonden!")
            
            # Lees robot status
            print("\nLees robot status...")
            for i in range(10):
                state = robot.get_state()
                print(f"Status update {i+1}: {state}")
                time.sleep(0.5)
            
            print("\nDemo voltooid!")
            
    except Exception as e:
        print(f"Fout: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

