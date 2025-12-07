#!/usr/bin/env python3
"""
PyBullet Simulatie Voorbeeld voor Unitree Go2 EDU

Demonstreert hoe je de Go2 robot kunt simuleren in PyBullet.
"""

import sys
import os
import time
from pathlib import Path

# Voeg parent directory toe aan path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.simulation import Go2Simulator
except ImportError as e:
    print(f"ERROR: {e}")
    print("\nInstalleer PyBullet met: pip install pybullet")
    sys.exit(1)


def basic_simulation():
    """Basis simulatie - robot staat stil"""
    print("=" * 70)
    print("  PyBullet Simulatie - Basis")
    print("=" * 70)
    print("\nRobot wordt geladen...")
    
    with Go2Simulator(gui=True) as sim:
        print("\n✓ Simulatie gestart!")
        print("  - Robot staat in standaard positie")
        print("  - Druk Ctrl+C om te stoppen\n")
        
        try:
            # Simuleer 3 seconden (korter voor snellere tests)
            sim.run_simulation(3.0)
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulatie gestopt door gebruiker")


def movement_simulation():
    """Simulatie met beweging"""
    print("=" * 70)
    print("  PyBullet Simulatie - Beweging")
    print("=" * 70)
    print("\nRobot wordt geladen...")
    
    with Go2Simulator(gui=True) as sim:
        print("\n✓ Simulatie gestart!")
        print("  - Robot gaat bewegen")
        print("  - Druk Ctrl+C om te stoppen\n")
        
        try:
            # Haal joint namen op
            joint_states = sim.get_joint_states()
            joint_names = list(joint_states.keys())
            
            # Zoek been joints
            hip_joints = [name for name in joint_names if 'hip' in name.lower()]
            thigh_joints = [name for name in joint_names if 'thigh' in name.lower()]
            calf_joints = [name for name in joint_names if 'calf' in name.lower()]
            
            print(f"Gevonden joints:")
            print(f"  Hip: {len(hip_joints)}")
            print(f"  Thigh: {len(thigh_joints)}")
            print(f"  Calf: {len(calf_joints)}")
            
            # Simuleer beweging
            import numpy as np
            
            # Kortere simulatie (100 stappen = ~4 seconden)
            for step in range(100):
                # Sinus beweging voor been joints
                t = step * 0.1
                
                # Beweeg heupen
                targets = {}
                for hip_joint in hip_joints:
                    targets[hip_joint] = 0.2 * np.sin(t)
                
                # Beweeg dijen
                for thigh_joint in thigh_joints:
                    targets[thigh_joint] = 0.4 + 0.2 * np.sin(t + np.pi/4)
                
                # Beweeg kuiten
                for calf_joint in calf_joints:
                    targets[calf_joint] = -0.8 + 0.2 * np.sin(t + np.pi/2)
                
                # Stel alle targets tegelijk in (efficiënter)
                sim.set_joint_targets(targets)
                sim.step()
                time.sleep(1.0 / 60.0)  # 60 Hz simulatie (sneller)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulatie gestopt door gebruiker")


def sensor_simulation():
    """Simulatie met sensor data lezen"""
    print("=" * 70)
    print("  PyBullet Simulatie - Sensor Data")
    print("=" * 70)
    print("\nRobot wordt geladen...")
    
    with Go2Simulator(gui=True) as sim:
        print("\n✓ Simulatie gestart!")
        print("  - Lezen sensor data")
        print("  - Druk Ctrl+C om te stoppen\n")
        
        try:
            # Kortere simulatie (20 stappen)
            for step in range(20):
                # Haal joint states op
                joint_states = sim.get_joint_states()
                
                # Haal base pose op
                position, orientation = sim.get_base_pose()
                linear_vel, angular_vel = sim.get_base_velocity()
                
                if step % 5 == 0:
                    print(f"\nStep {step}:")
                    print(f"  Positie: [{position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}]")
                    print(f"  Snelheid: [{linear_vel[0]:.3f}, {linear_vel[1]:.3f}, {linear_vel[2]:.3f}]")
                    
                    # Toon eerste paar joints
                    joint_names = list(joint_states.keys())[:3]
                    for name in joint_names:
                        pos = joint_states[name]['position']
                        vel = joint_states[name]['velocity']
                        print(f"  {name}: pos={pos:.3f}, vel={vel:.3f}")
                
                sim.step()
                time.sleep(1.0 / 60.0)  # 60 Hz simulatie (sneller)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulatie gestopt door gebruiker")


def main():
    """Hoofdfunctie"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='PyBullet simulatie voor Unitree Go2 EDU'
    )
    parser.add_argument(
        'mode',
        choices=['basic', 'movement', 'sensor'],
        nargs='?',
        default='basic',
        help='Simulatie modus (default: basic)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run zonder GUI (headless mode)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'basic':
        basic_simulation()
    elif args.mode == 'movement':
        movement_simulation()
    elif args.mode == 'sensor':
        sensor_simulation()
    else:
        print(f"Onbekende modus: {args.mode}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

