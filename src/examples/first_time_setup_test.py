#!/usr/bin/env python3
"""
First Time Setup Test voor Go2 Robot

Test script voor eerste keer gebruik - checkt alles en test robot verbinding.
Gebruikt de officiële SDK.
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def print_header(text):
    """Print een mooie header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(text):
    """Print een sectie header"""
    print(f"\n▶️  {text}")
    print("-" * 70)

def check_mark(condition, message):
    """Print check mark of cross"""
    if condition:
        print(f"  ✓ {message}")
        return True
    else:
        print(f"  ❌ {message}")
        return False

def test_imports():
    """Test of alle imports werken"""
    print_section("Test Imports")
    
    results = []
    
    # Test Go2Robot
    try:
        from src.unitree_go2 import Go2Robot, Go2ConnectionError, Go2CommandError, Go2TimeoutError
        results.append(check_mark(True, "Go2Robot import succesvol"))
    except ImportError as e:
        results.append(check_mark(False, f"Go2Robot import mislukt: {e}"))
    
    # Test HAS_OFFICIAL_SDK
    try:
        from src.unitree_go2 import HAS_OFFICIAL_SDK
        if HAS_OFFICIAL_SDK:
            results.append(check_mark(True, "Officiële SDK (CycloneDDS) beschikbaar"))
        else:
            results.append(check_mark(False, "Officiële SDK niet beschikbaar - check CYCLONEDDS_HOME"))
    except ImportError as e:
        results.append(check_mark(False, f"SDK check mislukt: {e}"))
    
    # Test andere modules
    try:
        from src.unitree_go2 import FlowExecutor
        results.append(check_mark(True, "FlowExecutor module beschikbaar"))
    except ImportError as e:
        results.append(check_mark(False, f"FlowExecutor import: {e}"))
    
    return all(results)

def test_python_version():
    """Test Python versie (moet 3.8-3.12 zijn voor cyclonedds)"""
    print_section("Test Python Versie")
    
    results = []
    
    python_version = sys.version_info
    version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    
    if python_version.major == 3 and 8 <= python_version.minor <= 12:
        results.append(check_mark(True, f"Python versie OK: {version_str}"))
    elif python_version.major == 3 and python_version.minor >= 13:
        results.append(check_mark(False, f"Python versie {version_str} mogelijk niet compatibel met cyclonedds"))
        print("  ⚠️  Python 3.13+ kan compatibiliteitsproblemen hebben met cyclonedds")
        print("  💡 Tip: Gebruik Python 3.12:")
        print("     python3.12 -m venv venv && source venv/bin/activate")
    else:
        results.append(check_mark(False, f"Python versie {version_str} mogelijk niet compatibel"))
        print("  💡 Tip: Gebruik Python 3.8-3.12 voor beste compatibiliteit")
    
    return all(results)

def test_cyclonedds():
    """Test CycloneDDS installatie"""
    print_section("Test CycloneDDS")
    
    results = []
    
    # Check CYCLONEDDS_HOME
    cyclonedds_home = os.getenv("CYCLONEDDS_HOME")
    if cyclonedds_home:
        results.append(check_mark(True, f"CYCLONEDDS_HOME gezet: {cyclonedds_home}"))
        
        # Check of directory bestaat
        if Path(cyclonedds_home).exists():
            results.append(check_mark(True, f"CycloneDDS directory bestaat"))
        else:
            results.append(check_mark(False, f"CycloneDDS directory niet gevonden"))
    else:
        results.append(check_mark(False, "CYCLONEDDS_HOME niet gezet"))
        print("  💡 Tip: ./install_cyclonedds_macos.sh")
        print("     of: export CYCLONEDDS_HOME=\"$HOME/cyclonedds/install\"")
    
    # Test cyclonedds import
    try:
        import cyclonedds
        results.append(check_mark(True, "cyclonedds Python package geïnstalleerd"))
    except ImportError:
        results.append(check_mark(False, "cyclonedds Python package niet geïnstalleerd"))
        print("  💡 Tip: pip install cyclonedds==0.10.2")
    
    return all(results)

def test_network_connection(ip_address="192.168.123.161"):
    """Test netwerk verbinding met robot"""
    print_section(f"Test Netwerk Verbinding ({ip_address})")
    
    import socket
    import subprocess
    
    results = []
    
    # Ping test
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2000", ip_address],
            capture_output=True,
            timeout=3
        )
        if result.returncode == 0:
            results.append(check_mark(True, f"Ping naar {ip_address} succesvol"))
        else:
            results.append(check_mark(False, f"Ping naar {ip_address} mislukt"))
            print("  💡 Tip: Zorg dat robot aan is en op hetzelfde netwerk zit")
    except Exception as e:
        results.append(check_mark(False, f"Ping test mislukt: {e}"))
    
    return all(results)

def test_robot_connection(ip_address="192.168.123.161", network_interface=None):
    """Test robot verbinding via officiële SDK"""
    print_section("Test Robot Verbinding")
    
    try:
        from src.unitree_go2 import Go2Robot, Go2ConnectionError, HAS_OFFICIAL_SDK
        
        if not HAS_OFFICIAL_SDK:
            check_mark(False, "Officiële SDK niet beschikbaar")
            print("  💡 Tip: Installeer CycloneDDS eerst")
            return False
        
        # Detecteer netwerk interface als niet opgegeven
        if not network_interface:
            import platform
            network_interface = "en0" if platform.system() == "Darwin" else "eth0"
        
        print(f"  📡 Netwerk interface: {network_interface}")
        
        robot = Go2Robot(
            ip_address=ip_address,
            network_interface=network_interface
        )
        
        try:
            robot.connect()
            check_mark(True, "Verbinding succesvol")
            
            # Test stand
            print("  ⏳ Test stand commando...")
            robot.stand()
            check_mark(True, "Stand commando verstuurd")
            time.sleep(1.0)
            
            # Test stop
            robot.stop()
            check_mark(True, "Stop commando verstuurd")
            
            robot.disconnect()
            return True
            
        except Go2ConnectionError as e:
            check_mark(False, f"Verbindingsfout: {e}")
            return False
        except Exception as e:
            check_mark(False, f"Fout: {e}")
            return False
            
    except ImportError as e:
        check_mark(False, f"Import fout: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="First Time Setup Test voor Go2 Robot"
    )
    parser.add_argument(
        "-i", "--ip",
        type=str,
        default="192.168.123.161",
        help="Robot IP adres (default: 192.168.123.161)"
    )
    parser.add_argument(
        "--interface",
        type=str,
        default=None,
        help="Netwerk interface naam (bijv. en0, eth0)"
    )
    parser.add_argument(
        "--skip-robot",
        action="store_true",
        help="Skip robot verbinding tests"
    )
    
    args = parser.parse_args()
    
    print_header("Go2 Robot - First Time Setup Test")
    print("\nDit script test of alles correct is geïnstalleerd.")
    print("Gebruikt de officiële Unitree SDK.\n")
    
    # Test 1: Python versie
    python_ok = test_python_version()
    
    # Test 2: CycloneDDS
    cyclonedds_ok = test_cyclonedds()
    
    # Test 3: Imports
    imports_ok = test_imports()
    
    # Test 4: Netwerk verbinding
    network_ok = False
    if not args.skip_robot:
        network_ok = test_network_connection(args.ip)
    
    # Test 5: Robot verbinding
    robot_ok = False
    if network_ok and cyclonedds_ok and not args.skip_robot:
        print("\n⚠️  Let op: Robot tests zullen commando's naar de robot sturen!")
        print("Zorg dat de robot aan is en er voldoende ruimte is.")
        try:
            response = input("\nDoorgaan met robot tests? (y/n): ")
            if response.lower() == 'y':
                robot_ok = test_robot_connection(args.ip, args.interface)
            else:
                print("  ⏭️  Robot tests overgeslagen")
        except KeyboardInterrupt:
            print("\n  ⏭️  Robot tests overgeslagen")
    elif args.skip_robot:
        print("\n  ⏭️  Robot tests overgeslagen (--skip-robot flag)")
    
    # Samenvatting
    print_header("Test Samenvatting")
    
    print("\n📋 Resultaten:")
    print(f"  {'✓' if python_ok else '❌'} Python Versie")
    print(f"  {'✓' if cyclonedds_ok else '❌'} CycloneDDS")
    print(f"  {'✓' if imports_ok else '❌'} Imports")
    if not args.skip_robot:
        print(f"  {'✓' if network_ok else '❌'} Netwerk")
        print(f"  {'✓' if robot_ok else '❌'} Robot Verbinding")
    
    # Aanbevelingen
    if not (python_ok and cyclonedds_ok and imports_ok):
        print("\n💡 Aanbevelingen:")
        
        if not python_ok:
            print("  - Gebruik Python 3.12: python3.12 -m venv venv")
        
        if not cyclonedds_ok:
            print("  - Installeer CycloneDDS: ./install_cyclonedds_macos.sh")
        
        if not imports_ok:
            print("  - Check dependencies: pip install -r requirements.txt")
    
    # Eindresultaat
    all_tests = [python_ok, cyclonedds_ok, imports_ok]
    if not args.skip_robot:
        all_tests.extend([network_ok, robot_ok])
    
    if all(all_tests):
        print("\n" + "=" * 70)
        print("  ✅ ALLE TESTS GESLAAGD!")
        print("=" * 70)
        print("\nJe kunt nu beginnen met de robot!")
        return 0
    else:
        print("\n" + "=" * 70)
        print("  ⚠️  SOMMIGE TESTS MISLUKT")
        print("=" * 70)
        print("\nLos de bovenstaande problemen op voordat je verder gaat.")
        return 1

if __name__ == "__main__":
    exit(main())
