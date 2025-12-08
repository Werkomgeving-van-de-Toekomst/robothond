#!/usr/bin/env python3
"""
Run getrainde RL modellen op fysieke Go2 robot

Laadt en gebruikt getrainde RL modellen om de fysieke Go2 robot te besturen.
"""

import sys
import os
from pathlib import Path
import argparse
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.unitree_go2.robot import Go2Robot
from src.unitree_go2.rl_controller import Go2RLController, Go2ModelManager


def run_single_model(model_path: str, max_steps: int = 1000, frequency: float = 20.0):
    """Run één model op robot"""
    
    print("=" * 70)
    print("  RL Model op Fysieke Go2 Robot")
    print("=" * 70)
    print(f"\nModel: {model_path}")
    print(f"Max steps: {max_steps}")
    print(f"Frequency: {frequency}Hz\n")
    
    # Connect met robot
    print("✓ Verbinden met Go2 robot...")
    robot = Go2Robot()
    
    try:
        robot.connect()
        print("✓ Verbonden met robot")
        
        # Laad RL model
        controller = Go2RLController(robot, model_path)
        
        # Run episode
        print("\n✓ Episode starten...")
        print("  Druk Ctrl+C om te stoppen\n")
        
        controller.run_episode(max_steps=max_steps, frequency=frequency)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Gestopt door gebruiker")
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n✓ Verbinding sluiten...")
        robot.disconnect()


def run_multiple_models(
    models: dict,
    switch_after_steps: int = 500,
    frequency: float = 20.0
):
    """
    Run meerdere modellen en wissel tussen hen
    
    Args:
        models: Dictionary met {name: model_path}
        switch_after_steps: Aantal stappen voor wisselen
        frequency: Control frequentie in Hz
    """
    
    print("=" * 70)
    print("  Meerdere RL Modellen op Fysieke Go2 Robot")
    print("=" * 70)
    print(f"\nModellen: {list(models.keys())}")
    print(f"Wissel na: {switch_after_steps} stappen")
    print(f"Frequency: {frequency}Hz\n")
    
    # Connect met robot
    print("✓ Verbinden met Go2 robot...")
    robot = Go2Robot()
    
    try:
        robot.connect()
        print("✓ Verbonden met robot")
        
        # Laad alle modellen
        manager = Go2ModelManager(robot)
        
        for name, model_path in models.items():
            manager.load_model(name, model_path)
        
        print(f"\n✓ {len(manager.list_models())} modellen geladen")
        
        # Wissel tussen modellen
        model_names = list(models.keys())
        current_index = 0
        
        print("\n✓ Episode starten...")
        print("  Druk Ctrl+C om te stoppen\n")
        
        step_count = 0
        
        while True:
            # Wissel model indien nodig
            if step_count % switch_after_steps == 0:
                model_name = model_names[current_index % len(model_names)]
                controller = manager.switch_model(model_name)
                print(f"\n[{step_count}] Gewisseld naar: {model_name}")
                current_index += 1
            
            # Voer stap uit
            controller = manager.get_current_controller()
            if controller:
                controller.step()
                step_count += 1
                
                if step_count % 100 == 0:
                    print(f"  Step {step_count} - Model: {manager.current_model}")
                
                time.sleep(1.0 / frequency)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Gestopt door gebruiker")
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n✓ Verbinding sluiten...")
        robot.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description="Run getrainde RL modellen op fysieke Go2 robot"
    )
    parser.add_argument(
        "model_path",
        type=str,
        nargs="?",
        default=None,
        help="Pad naar getraind model (of gebruik --models voor meerdere)"
    )
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        help="Meerdere modellen in formaat: name1:path1 name2:path2"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
        help="Maximum aantal stappen (default: 1000)"
    )
    parser.add_argument(
        "--frequency",
        type=float,
        default=20.0,
        help="Control frequentie in Hz (default: 20.0)"
    )
    parser.add_argument(
        "--switch-after",
        type=int,
        default=500,
        help="Aantal stappen voor wisselen tussen modellen (default: 500)"
    )
    
    args = parser.parse_args()
    
    if args.models:
        # Meerdere modellen
        models_dict = {}
        for model_spec in args.models:
            if ":" in model_spec:
                name, path = model_spec.split(":", 1)
                models_dict[name] = path
            else:
                # Alleen pad, gebruik bestandsnaam als naam
                name = Path(model_spec).stem
                models_dict[name] = model_spec
        
        run_multiple_models(
            models=models_dict,
            switch_after_steps=args.switch_after,
            frequency=args.frequency
        )
    elif args.model_path:
        # Enkel model
        run_single_model(
            model_path=args.model_path,
            max_steps=args.max_steps,
            frequency=args.frequency
        )
    else:
        parser.print_help()
        print("\nERROR: Geef een model_path of --models op")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

