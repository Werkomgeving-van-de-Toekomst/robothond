#!/usr/bin/env python3
"""
Snelle PyBullet test - korte demonstratie
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.simulation import Go2Simulator
import time
import numpy as np

print("="*70)
print("  Snelle PyBullet Test - 5 seconden")
print("="*70)

with Go2Simulator(gui=True) as sim:
    print(f"✓ Robot geladen: {len(sim.joint_indices)} joints")
    
    # Korte beweging test
    hip_joints = [n for n in sim.joint_names if 'hip' in n.lower()][:2]  # Alleen eerste 2
    
    print(f"\nBeweeg {len(hip_joints)} joints gedurende 3 seconden...")
    
    start_time = time.time()
    step = 0
    
    while time.time() - start_time < 3.0:
        t = step * 0.1
        targets = {}
        
        for joint in hip_joints:
            targets[joint] = 0.2 * np.sin(t)
        
        sim.set_joint_targets(targets)
        sim.step()
        time.sleep(1.0 / 60.0)  # 60 Hz
        step += 1
    
    print("✓ Test voltooid!")

