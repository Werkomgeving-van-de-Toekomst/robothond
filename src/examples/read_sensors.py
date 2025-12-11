"""
Sensor data lezen voorbeeld voor Unitree Go2 EDU

Dit script demonstreert hoe je sensor data van de robot kunt lezen.
"""

import sys
import os
import time

# Voeg parent directory toe aan path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.unitree_go2 import Go2Robot


def main():
    """Sensor data lezen demo"""
    
    # IP adres van je robot (pas aan indien nodig)
    robot_ip = "192.168.123.161"
    
    print(f"Verbinden met robot op {robot_ip}...")
    
    try:
        # Maak verbinding met robot
        with Go2Robot(ip_address=robot_ip) as robot:
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

