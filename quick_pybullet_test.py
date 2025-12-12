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

# Detecteer of GUI beschikbaar is
def has_display():
    """Check of er een X11 display beschikbaar is"""
    return os.environ.get('DISPLAY') is not None

# Bepaal GUI mode: gebruik command-line argument of auto-detect
gui_mode = True
if len(sys.argv) > 1:
    if sys.argv[1] in ['--no-gui', '--headless', '-n']:
        gui_mode = False
    elif sys.argv[1] in ['--gui', '-g']:
        gui_mode = True
else:
    # Auto-detect: alleen GUI als DISPLAY beschikbaar is
    gui_mode = has_display()

print("="*70)
print("  Snelle PyBullet Test - 5 seconden")
print("="*70)
print(f"  GUI mode: {'AAN' if gui_mode else 'UIT (headless)'}")
print("="*70)

with Go2Simulator(gui=gui_mode) as sim:
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

