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
    # Probeer eerst geoptimaliseerde versie voor Apple Silicon
    try:
        from src.simulation.go2_simulator_optimized import Go2SimulatorOptimized as Go2Simulator
    except ImportError:
        from src.simulation import Go2Simulator
    import pybullet as p
except ImportError as e:
    print(f"ERROR: {e}")
    print("\nInstalleer PyBullet met: conda install -c conda-forge pybullet")
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
                # Geen sleep nodig - PyBullet regelt timing zelf voor betere performance
                # time.sleep(1.0 / 60.0)  # 60 Hz simulatie (sneller)
                
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
                # Geen sleep nodig - PyBullet regelt timing zelf voor betere performance
                # time.sleep(1.0 / 60.0)  # 60 Hz simulatie (sneller)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulatie gestopt door gebruiker")


def circle_walk_simulation():
    """Simulatie waarbij de robot in een kring loopt"""
    print("=" * 70)
    print("  PyBullet Simulatie - Cirkel Lopen")
    print("=" * 70)
    print("\nRobot wordt geladen...")
    
    with Go2Simulator(gui=True) as sim:
        print("\n✓ Simulatie gestart!")
        print("  - Robot loopt in een cirkel")
        print("  - Druk Ctrl+C om te stoppen\n")
        
        try:
            import numpy as np
            
            # Haal joint namen op
            joint_states = sim.get_joint_states()
            joint_names = list(joint_states.keys())
            
            # Organiseer joints per been
            # FL = Front Left, FR = Front Right, RL = Rear Left, RR = Rear Right
            legs = {
                'FL': [name for name in joint_names if name.startswith('FL_')],
                'FR': [name for name in joint_names if name.startswith('FR_')],
                'RL': [name for name in joint_names if name.startswith('RL_')],
                'RR': [name for name in joint_names if name.startswith('RR_')]
            }
            
            print(f"Gevonden benen:")
            for leg_name, leg_joints in legs.items():
                print(f"  {leg_name}: {len(leg_joints)} joints")
            
            # Cirkel parameters
            circle_radius = 1.0  # meter
            circle_speed = 0.3  # rad/s (hoek snelheid)
            walk_frequency = 2.0  # Hz (stap frequentie)
            
            # Loop parameters
            step_height = 0.05  # Hoogte van stap
            step_length = 0.1  # Lengte van stap
            
            # Start positie
            start_pos, _ = sim.get_base_pose()
            print(f"\nStart positie: [{start_pos[0]:.2f}, {start_pos[1]:.2f}, {start_pos[2]:.2f}]")
            print(f"Cirkel straal: {circle_radius}m")
            print(f"Loop snelheid: {circle_speed} rad/s\n")
            
            # Simuleer circulaire beweging
            for step in range(500):  # ~2 seconden bij 240Hz
                t = step * (1.0 / 240.0)  # Tijd in seconden
                
                # Bereken positie op cirkel
                angle = circle_speed * t
                target_x = circle_radius * np.cos(angle)
                target_y = circle_radius * np.sin(angle)
                
                # Huidige positie
                current_pos, current_ori = sim.get_base_pose()
                
                # Bereken gewenste orientatie (kijk naar centrum)
                target_yaw = angle + np.pi / 2  # Loodrecht op radius
                
                # Stel base positie en orientatie in (voor visualisatie)
                # In echte simulatie zou dit via krachten gebeuren, maar voor demo gebruiken we directe controle
                import pybullet as p
                target_orientation = p.getQuaternionFromEuler([0, 0, target_yaw])
                
                # Trotting gait: diagonale benen bewegen samen
                # FL + RR bewegen samen, FR + RL bewegen samen
                phase = (t * walk_frequency * 2 * np.pi) % (2 * np.pi)
                
                # Bereken joint targets voor trotting gait
                targets = {}
                
                for leg_name, leg_joints in legs.items():
                    # Bepaal fase offset voor dit been
                    if leg_name in ['FL', 'RR']:
                        leg_phase = phase
                    else:  # FR, RL
                        leg_phase = phase + np.pi
                    
                    # Hip joint: voor/achter beweging
                    hip_joint = [j for j in leg_joints if 'hip' in j.lower()][0]
                    thigh_joint = [j for j in leg_joints if 'thigh' in j.lower()][0]
                    calf_joint = [j for j in leg_joints if 'calf' in j.lower()][0]
                    
                    # Swing fase (been omhoog)
                    if np.sin(leg_phase) > 0:
                        # Been is in swing fase
                        swing_progress = (np.sin(leg_phase) + 1) / 2  # 0 tot 1
                        
                        # Hip: beweeg vooruit
                        targets[hip_joint] = step_length * np.sin(leg_phase)
                        
                        # Thigh: til been op
                        targets[thigh_joint] = 0.4 + step_height * swing_progress
                        
                        # Calf: buig been
                        targets[calf_joint] = -0.8 + 0.3 * swing_progress
                    else:
                        # Been is in stance fase (op grond)
                        stance_progress = (-np.sin(leg_phase) + 1) / 2  # 0 tot 1
                        
                        # Hip: terug naar neutraal
                        targets[hip_joint] = -step_length * stance_progress
                        
                        # Thigh: normale positie
                        targets[thigh_joint] = 0.4
                        
                        # Calf: strek been
                        targets[calf_joint] = -0.8
                
                # Stel alle joint targets in
                sim.set_joint_targets(targets)
                
                # Update base positie voor circulaire beweging
                # In echte robot zou dit via krachten gebeuren, maar voor demo gebruiken we directe controle
                new_pos = [target_x, target_y, start_pos[2]]
                p.resetBasePositionAndOrientation(
                    sim.robot_id,
                    new_pos,
                    target_orientation
                )
                
                # Simuleer stap
                sim.step()
                
                # Print status elke seconde
                if step % 240 == 0:
                    dist_from_center = np.sqrt(current_pos[0]**2 + current_pos[1]**2)
                    print(f"Tijd: {t:.2f}s | Positie: [{current_pos[0]:.2f}, {current_pos[1]:.2f}] | Afstand tot centrum: {dist_from_center:.2f}m")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulatie gestopt door gebruiker")
        except Exception as e:
            print(f"\n❌ Fout: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Hoofdfunctie"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='PyBullet simulatie voor Unitree Go2 EDU'
    )
    parser.add_argument(
        'mode',
        choices=['basic', 'movement', 'sensor', 'circle'],
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
    elif args.mode == 'circle':
        circle_walk_simulation()
    else:
        print(f"Onbekende modus: {args.mode}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

