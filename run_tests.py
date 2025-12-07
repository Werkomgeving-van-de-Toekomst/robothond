#!/usr/bin/env python3
"""
Test runner voor Unitree Go2 EDU SDK tests

Voert alle tests uit en genereert een rapport.
"""

import sys
import os
import time
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


def print_header(text):
    """Print een mooie header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_section(text):
    """Print een sectie header"""
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print(f"{'─' * 70}\n")


def run_tests(test_categories=None, verbose=False, robot_ip=None):
    """
    Voer tests uit
    
    Args:
        test_categories: Lijst van test categorieën om uit te voeren
        verbose: Verbose output
        robot_ip: IP adres van robot (overschrijft configuratie)
    """
    print_header("Unitree Go2 EDU SDK Test Suite")
    
    # Test configuratie
    if robot_ip:
        os.environ['GO2_ROBOT_IP'] = robot_ip
        print(f"Robot IP adres: {robot_ip}")
    else:
        print("Robot IP adres: 192.168.123.161 (standaard)")
    
    print(f"Starttijd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test categorieën
    all_categories = {
        'connection': 'tests/test_connection.py',
        'commands': 'tests/test_commands.py',
        'sensors': 'tests/test_sensors.py',
        'errors': 'tests/test_error_handling.py',
        'performance': 'tests/test_performance.py',
        'all': None  # Alle tests
    }
    
    if test_categories is None:
        test_categories = ['all']
    
    # Voer tests uit per categorie
    results = {}
    total_start = time.time()
    
    for category in test_categories:
        if category not in all_categories:
            print(f"⚠️  Onbekende test categorie: {category}")
            continue
        
        if category == 'all':
            print_section("Alle Tests")
            test_path = 'tests/'
        else:
            print_section(f"Tests: {category.upper()}")
            test_path = all_categories[category]
        
        # Voer pytest uit
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
    print_header("Test Samenvatting")
    
    print(f"{'Categorie':<20} {'Status':<15} {'Tijd':<10}")
    print("-" * 70)
    
    for category, result in results.items():
        status = "✓ GESLAAGD" if result['success'] else "✗ GEFAALD"
        print(f"{category:<20} {status:<15} {result['elapsed_time']:.2f}s")
    
    print("-" * 70)
    print(f"{'TOTAAL':<20} {'':<15} {total_time:.2f}s")
    
    # Eindstatus
    all_passed = all(r['success'] for r in results.values())
    
    print_header("Eindresultaat")
    
    if all_passed:
        print("✓ ALLE TESTS GESLAAGD!")
        print("\nDe SDK werkt correct met je robot.")
    else:
        print("✗ SOMIGE TESTS GEFAALD")
        print("\nControleer de output hierboven voor details.")
        print("Mogelijke oorzaken:")
        print("  - Robot niet verbonden")
        print("  - Verkeerd IP adres")
        print("  - SDK protocol niet correct geïmplementeerd")
        print("  - Robot niet in ontwikkelaarsmodus")
    
    print(f"\nEindtijd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if all_passed else 1


def main():
    """Hoofdfunctie"""
    parser = argparse.ArgumentParser(
        description='Voer Unitree Go2 EDU SDK tests uit'
    )
    parser.add_argument(
        '-c', '--category',
        action='append',
        choices=['connection', 'commands', 'sensors', 'errors', 'performance', 'all'],
        help='Test categorie om uit te voeren (kan meerdere keren gebruikt worden)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '-i', '--ip',
        type=str,
        help='IP adres van de robot (overschrijft configuratie)'
    )
    
    args = parser.parse_args()
    
    test_categories = args.category if args.category else ['all']
    
    exit_code = run_tests(
        test_categories=test_categories,
        verbose=args.verbose,
        robot_ip=args.ip
    )
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

