"""
Basis beweging voorbeeld voor Unitree Go2 EDU

Dit script demonstreert hoe je de robot kunt laten bewegen.
"""

import sys
import os
import time

# Voeg parent directory toe aan path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.unitree_go2 import Go2Robot


def main():
    """Basis beweging demo"""
    
    # IP adres van je robot (pas aan indien nodig)
    robot_ip = "192.168.123.161"
    
    print(f"Verbinden met robot op {robot_ip}...")
    
    try:
        # Maak verbinding met robot
        with Go2Robot(ip_address=robot_ip) as robot:
            print("Verbonden!")
            
            # Laat robot rechtop staan
            print("Robot gaat rechtop staan...")
            robot.stand()
            time.sleep(2)
            
            # Beweeg vooruit
            print("Beweeg vooruit...")
            robot.move(vx=0.3, vy=0.0, vyaw=0.0)
            time.sleep(3)
            
            # Stop
            print("Stoppen...")
            robot.stop()
            time.sleep(1)
            
            # Draai
            print("Draaien...")
            robot.move(vx=0.0, vy=0.0, vyaw=0.5)
            time.sleep(2)
            
            # Stop
            print("Stoppen...")
            robot.stop()
            time.sleep(1)
            
            # Laat robot zitten
            print("Robot gaat zitten...")
            robot.sit()
            time.sleep(2)
            
            print("Demo voltooid!")
            
    except Exception as e:
        print(f"Fout: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

