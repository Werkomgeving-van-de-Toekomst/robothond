#!/usr/bin/env python3
"""
Snelle PyBullet test script
Test verschillende functies van de Go2 simulator
"""

import sys
import os
import time
import numpy as np
from pathlib import Path

# Voeg project root toe aan path
sys.path.insert(0, str(Path(__file__).parent))

from src.simulation import Go2Simulator


def test_basic():
    """Test 1: Basis simulatie - robot staat stil"""
    print("\n" + "="*70)
    print("TEST 1: Basis Simulatie")
    print("="*70)
    
    with Go2Simulator(gui=True) as sim:
        print("✓ Robot geladen")
        print(f"  - Aantal joints: {len(sim.joint_indices)}")
        print(f"  - Joint namen: {sim.joint_names[:6]}...")
        
        # Wacht 3 seconden
        print("\nSimuleer 3 seconden...")
        sim.run_simulation(3.0)
        print("✓ Test voltooid")


def test_joint_control():
    """Test 2: Joint control - beweeg individuele joints"""
    print("\n" + "="*70)
    print("TEST 2: Joint Control")
    print("="*70)
    
    with Go2Simulator(gui=True) as sim:
        print("✓ Robot geladen")
        
        # Zoek een hip joint
        hip_joints = [name for name in sim.joint_names if 'hip' in name.lower()]
        if hip_joints:
            test_joint = hip_joints[0]
            print(f"\nTest joint: {test_joint}")
            
            # Beweeg heen en weer
            for i in range(20):
                angle = 0.3 * np.sin(i * 0.2)
                sim.set_joint_targets({test_joint: angle})
                sim.step()
                time.sleep(0.05)
            
            print("✓ Joint beweging getest")


def test_multiple_joints():
    """Test 3: Meerdere joints tegelijk"""
    print("\n" + "="*70)
    print("TEST 3: Meerdere Joints")
    print("="*70)
    
    with Go2Simulator(gui=True) as sim:
        print("✓ Robot geladen")
        
        # Zoek joints per type
        hip_joints = [name for name in sim.joint_names if 'hip' in name.lower()]
        thigh_joints = [name for name in sim.joint_names if 'thigh' in name.lower()]
        calf_joints = [name for name in sim.joint_names if 'calf' in name.lower()]
        
        print(f"\nGevonden:")
        print(f"  - Hip joints: {len(hip_joints)}")
        print(f"  - Thigh joints: {len(thigh_joints)}")
        print(f"  - Calf joints: {len(calf_joints)}")
        
        # Beweeg alle benen synchroon
        print("\nBeweeg alle benen...")
        for step in range(50):
            t = step * 0.1
            
            targets = {}
            # Hip beweging
            for joint in hip_joints:
                targets[joint] = 0.2 * np.sin(t)
            
            # Thigh beweging
            for joint in thigh_joints:
                targets[joint] = 0.4 + 0.2 * np.sin(t + np.pi/4)
            
            # Calf beweging
            for joint in calf_joints:
                targets[joint] = -0.8 + 0.2 * np.sin(t + np.pi/2)
            
            sim.set_joint_targets(targets)
            sim.step()
            time.sleep(1.0 / 60.0)  # 60 Hz
        
        print("✓ Multi-joint beweging getest")


def test_sensor_data():
    """Test 4: Sensor data lezen"""
    print("\n" + "="*70)
    print("TEST 4: Sensor Data")
    print("="*70)
    
    with Go2Simulator(gui=True) as sim:
        print("✓ Robot geladen")
        
        print("\nLees sensor data (10 stappen)...")
        for i in range(10):
            # Joint states
            joint_states = sim.get_joint_states()
            
            # Base pose
            position, orientation = sim.get_base_pose()
            linear_vel, angular_vel = sim.get_base_velocity()
            
            if i % 2 == 0:
                print(f"\nStep {i}:")
                print(f"  Positie: [{position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}]")
                print(f"  Snelheid: [{linear_vel[0]:.3f}, {linear_vel[1]:.3f}, {linear_vel[2]:.3f}]")
                
                # Toon eerste 3 joints
                joint_names = list(joint_states.keys())[:3]
                for name in joint_names:
                    pos = joint_states[name]['position']
                    print(f"  {name}: {pos:.3f} rad")
            
            sim.step()
            time.sleep(0.1)
        
        print("✓ Sensor data lezen getest")


def test_reset():
    """Test 5: Reset functionaliteit"""
    print("\n" + "="*70)
    print("TEST 5: Reset Functionaliteit")
    print("="*70)
    
    with Go2Simulator(gui=True) as sim:
        print("✓ Robot geladen")
        
        # Beweeg een joint
        hip_joints = [name for name in sim.joint_names if 'hip' in name.lower()]
        if hip_joints:
            print(f"\nBeweeg {hip_joints[0]} naar 0.5 rad...")
            sim.set_joint_targets({hip_joints[0]: 0.5})
            sim.run_simulation(1.0)
            
            # Check positie
            joint_states = sim.get_joint_states()
            pos_before = joint_states[hip_joints[0]]['position']
            print(f"  Positie voor reset: {pos_before:.3f} rad")
            
            # Reset
            print("\nReset robot...")
            sim.reset()
            sim.run_simulation(0.5)
            
            # Check positie na reset
            joint_states = sim.get_joint_states()
            pos_after = joint_states[hip_joints[0]]['position']
            print(f"  Positie na reset: {pos_after:.3f} rad")
            
            print("✓ Reset functionaliteit getest")


def main():
    """Voer alle tests uit"""
    print("\n" + "="*70)
    print("  PyBullet Go2 Simulator Tests")
    print("="*70)
    print("\nDit script test verschillende functies van de Go2 simulator.")
    print("Elke test opent een PyBullet venster.")
    print("Druk Ctrl+C om een test te stoppen.\n")
    
    tests = [
        ("Basis Simulatie", test_basic),
        ("Joint Control", test_joint_control),
        ("Meerdere Joints", test_multiple_joints),
        ("Sensor Data", test_sensor_data),
        ("Reset", test_reset),
    ]
    
    print(f"\nBeschikbare tests:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"  {i}. {name}")
    
    print("\nVoer alle tests uit? (j/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice != 'j':
            print("Geannuleerd.")
            return
    except KeyboardInterrupt:
        print("\nGeannuleerd.")
        return
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"\n✓ {name} voltooid")
            time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n⚠️  {name} gestopt door gebruiker")
            break
        except Exception as e:
            print(f"\n❌ Fout in {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("  Alle tests voltooid!")
    print("="*70)


if __name__ == '__main__':
    main()

