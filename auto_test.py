#!/usr/bin/env python3
"""
Automatisch test script voor Unitree Go2 EDU

Wacht tot de robot verbonden is en voert dan automatisch alle tests uit.
"""

import sys
import os
import time
import socket
import argparse
from datetime import datetime
from pathlib import Path

# Voeg project root toe aan path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import pytest
except ImportError:
    print("ERROR: pytest niet geïnstalleerd. Installeer met: pip install pytest")
    sys.exit(1)

from src.unitree_go2 import Go2Robot, Go2ConnectionError


def check_robot_reachable(ip_address, port=8080, timeout=2):
    """
    Controleer of robot bereikbaar is via netwerk
    
    Returns:
        True als robot bereikbaar is, False anders
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.connect((ip_address, port))
        sock.close()
        return True
    except:
        return False


def wait_for_robot(ip_address, check_interval=2, max_wait_time=None):
    """
    Wacht tot robot bereikbaar is
    
    Args:
        ip_address: IP adres van robot
        check_interval: Tijd tussen checks in seconden
        max_wait_time: Maximale wachttijd in seconden (None = oneindig)
    
    Returns:
        True als robot bereikbaar wordt, False als timeout
    """
    print(f"🔍 Wachten op robot op {ip_address}...")
    print("   (Druk Ctrl+C om te annuleren)\n")
    
    start_time = time.time()
    attempt = 0
    
    while True:
        attempt += 1
        elapsed = time.time() - start_time
        
        # Check timeout
        if max_wait_time and elapsed > max_wait_time:
            print(f"\n⏱️  Timeout na {max_wait_time} seconden")
            return False
        
        # Check of robot bereikbaar is
        if check_robot_reachable(ip_address):
            print(f"✓ Robot gevonden na {elapsed:.1f} seconden ({attempt} pogingen)")
            return True
        
        # Status update elke 10 seconden
        if attempt % (5) == 0:
            print(f"   Poging {attempt}... ({elapsed:.1f}s)")
        
        time.sleep(check_interval)


def test_connection(ip_address):
    """
    Test basis verbinding met robot
    
    Returns:
        True als verbinding succesvol, False anders
    """
    try:
        robot = Go2Robot(ip_address=ip_address)
        robot.connect()
        robot.disconnect()
        return True
    except Exception as e:
        print(f"   ⚠️  Verbinding test: {e}")
        return False


def run_tests(ip_address, test_categories=None, verbose=False):
    """
    Voer tests uit
    
    Args:
        ip_address: IP adres van robot
        test_categories: Lijst van test categorieën
        verbose: Verbose output
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    # Set environment variable voor tests
    os.environ['GO2_ROBOT_IP'] = ip_address
    
    # Test categorieën
    all_categories = {
        'connection': 'tests/test_connection.py',
        'commands': 'tests/test_commands.py',
        'sensors': 'tests/test_sensors.py',
        'errors': 'tests/test_error_handling.py',
        'performance': 'tests/test_performance.py',
    }
    
    if test_categories is None:
        test_categories = list(all_categories.keys())
    
    print("\n" + "=" * 70)
    print("  Tests Uitvoeren")
    print("=" * 70 + "\n")
    
    results = {}
    total_start = time.time()
    
    for category in test_categories:
        if category not in all_categories:
            print(f"⚠️  Onbekende test categorie: {category}")
            continue
        
        print(f"\n📋 Test categorie: {category.upper()}")
        print("-" * 70)
        
        test_path = all_categories[category]
        pytest_args = [
            test_path,
            '-v' if verbose else '-q',
            '--tb=short',
            '--color=yes'
        ]
        
        start_time = time.time()
        exit_code = pytest.main(pytest_args)
        elapsed_time = time.time() - start_time
        
        results[category] = {
            'exit_code': exit_code,
            'elapsed_time': elapsed_time,
            'success': exit_code == 0
        }
        
        status = "✓ GESLAAGD" if exit_code == 0 else "✗ GEFAALD"
        print(f"\n{status} - {category} ({elapsed_time:.2f}s)")
    
    total_time = time.time() - total_start
    
    # Print samenvatting
    print("\n" + "=" * 70)
    print("  Test Samenvatting")
    print("=" * 70)
    
    print(f"\n{'Categorie':<20} {'Status':<15} {'Tijd':<10}")
    print("-" * 70)
    
    for category, result in results.items():
        status = "✓ GESLAAGD" if result['success'] else "✗ GEFAALD"
        print(f"{category:<20} {status:<15} {result['elapsed_time']:.2f}s")
    
    print("-" * 70)
    print(f"{'TOTAAL':<20} {'':<15} {total_time:.2f}s")
    
    # Eindstatus
    all_passed = all(r['success'] for r in results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("  ✓ ALLE TESTS GESLAAGD!")
    else:
        print("  ✗ SOMIGE TESTS GEFAALD")
    print("=" * 70)
    
    return 0 if all_passed else 1


def main():
    """Hoofdfunctie"""
    parser = argparse.ArgumentParser(
        description='Automatisch test script - wacht op robot en voer tests uit'
    )
    parser.add_argument(
        '-i', '--ip',
        type=str,
        default="192.168.123.161",
        help='IP adres van de robot'
    )
    parser.add_argument(
        '-c', '--category',
        action='append',
        choices=['connection', 'commands', 'sensors', 'errors', 'performance'],
        help='Test categorie om uit te voeren (kan meerdere keren gebruikt worden)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--check-interval',
        type=float,
        default=2.0,
        help='Tijd tussen verbindingschecks in seconden (default: 2.0)'
    )
    parser.add_argument(
        '--max-wait',
        type=int,
        default=None,
        help='Maximale wachttijd in seconden (default: oneindig)'
    )
    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='Wacht niet op robot, voer direct tests uit'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Voer tests continu uit (herhaal na elke cyclus)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Tijd tussen test cycli in seconden bij --continuous (default: 60)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  Unitree Go2 EDU Automatisch Test Script")
    print("=" * 70)
    print(f"\nRobot IP: {args.ip}")
    print(f"Starttijd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Wacht op robot (tenzij --no-wait)
    if not args.no_wait:
        if not wait_for_robot(args.ip, args.check_interval, args.max_wait):
            print("\n❌ Robot niet bereikbaar. Script gestopt.")
            sys.exit(1)
        
        # Test verbinding
        print("\n🔌 Testen verbinding...")
        if not test_connection(args.ip):
            print("⚠️  Verbinding test mislukt, maar doorgaan met tests...")
        else:
            print("✓ Verbinding OK\n")
    
    # Voer tests uit
    exit_code = 0
    
    try:
        if args.continuous:
            print("\n🔄 Continue modus: tests worden herhaald")
            print(f"   Interval tussen cycli: {args.interval} seconden")
            print("   Druk Ctrl+C om te stoppen\n")
            
            cycle = 1
            while True:
                print(f"\n{'='*70}")
                print(f"  Test Cyclus #{cycle}")
                print(f"{'='*70}")
                print(f"Tijd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Check of robot nog bereikbaar is
                if not check_robot_reachable(args.ip):
                    print("⚠️  Robot niet meer bereikbaar, wachten...")
                    wait_for_robot(args.ip, args.check_interval)
                
                # Voer tests uit
                cycle_exit_code = run_tests(
                    args.ip,
                    test_categories=args.category,
                    verbose=args.verbose
                )
                
                if cycle_exit_code != 0:
                    exit_code = cycle_exit_code
                
                cycle += 1
                
                print(f"\n⏳ Wachten {args.interval} seconden tot volgende cyclus...")
                print("   (Druk Ctrl+C om te stoppen)")
                time.sleep(args.interval)
        
        else:
            # Eenmalige test run
            exit_code = run_tests(
                args.ip,
                test_categories=args.category,
                verbose=args.verbose
            )
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Script gestopt door gebruiker")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Onverwachte fout: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\nEindtijd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

