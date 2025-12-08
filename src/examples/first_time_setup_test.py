#!/usr/bin/env python3
"""
First Time Setup Test voor Go2 Robot

Test script voor eerste keer gebruik - checkt alles en test robot verbinding.
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
    
    # Test custom wrapper
    try:
        from src.unitree_go2 import Go2Robot, Go2ConnectionError, Go2CommandError
        results.append(check_mark(True, "Custom wrapper (Go2Robot) import"))
    except ImportError as e:
        results.append(check_mark(False, f"Custom wrapper import: {e}"))
    
    # Test officiële SDK
    try:
        from src.unitree_go2 import HAS_OFFICIAL_SDK, Go2RobotOfficial
        if HAS_OFFICIAL_SDK:
            results.append(check_mark(True, "Officiële SDK (Go2RobotOfficial) beschikbaar"))
        else:
            results.append(check_mark(False, "Officiële SDK niet beschikbaar (check CYCLONEDDS_HOME)"))
    except ImportError as e:
        results.append(check_mark(False, f"Officiële SDK import: {e}"))
    
    # Test andere modules
    try:
        from src.unitree_go2 import FlowExecutor, WebSearcher
        results.append(check_mark(True, "Flow executor en web search modules"))
    except ImportError as e:
        results.append(check_mark(False, f"Extra modules import: {e}"))
    
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
            results.append(check_mark(False, f"CycloneDDS directory niet gevonden: {cyclonedds_home}"))
    else:
        results.append(check_mark(False, "CYCLONEDDS_HOME niet gezet"))
        print("  💡 Tip: export CYCLONEDDS_HOME=\"/Users/marc/cyclonedds/install\"")
    
    # Test cyclonedds import
    try:
        import cyclonedds
        results.append(check_mark(True, f"cyclonedds Python package geïnstalleerd (versie: {cyclonedds.__version__})"))
    except ImportError:
        results.append(check_mark(False, "cyclonedds Python package niet geïnstalleerd"))
        print("  💡 Tip: pip install cyclonedds==0.10.2 (na CYCLONEDDS_HOME te zetten)")
    
    return all(results)

def test_network_connection(ip_address="192.168.123.161"):
    """Test netwerk verbinding met robot"""
    print_section(f"Test Netwerk Verbinding ({ip_address})")
    
    import socket
    
    results = []
    
    # Ping test (simpele socket connect)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        # UDP heeft geen connect, maar we kunnen proberen te senden
        sock.sendto(b"test", (ip_address, 8080))
        sock.close()
        results.append(check_mark(True, f"Socket test naar {ip_address}:8080"))
    except Exception as e:
        results.append(check_mark(False, f"Socket test mislukt: {e}"))
    
    # Check of IP bereikbaar is (ping via subprocess)
    import subprocess
    try:
        # macOS/Linux ping
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

def test_custom_wrapper(ip_address="192.168.123.161"):
    """Test custom wrapper verbinding"""
    print_section("Test Custom Wrapper (Go2Robot)")
    
    try:
        from src.unitree_go2 import Go2Robot, Go2ConnectionError
        
        robot = Go2Robot(ip_address=ip_address)
        
        # Test connect
        try:
            robot.connect()
            check_mark(True, "Verbinding succesvol")
            
            # Test stand
            print("  ⏳ Test stand commando...")
            result = robot.stand()
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
            
    except ImportError:
        check_mark(False, "Custom wrapper niet beschikbaar")
        return False

def test_official_sdk(ip_address="192.168.123.161", network_interface=None):
    """Test officiële SDK verbinding"""
    print_section("Test Officiële SDK (Go2RobotOfficial)")
    
    try:
        from src.unitree_go2 import HAS_OFFICIAL_SDK, Go2RobotOfficial
        
        if not HAS_OFFICIAL_SDK:
            check_mark(False, "Officiële SDK niet beschikbaar")
            print("  💡 Tip: Zorg dat CYCLONEDDS_HOME gezet is en cyclonedds geïnstalleerd")
            return False
        
        # Detecteer netwerk interface als niet opgegeven
        if not network_interface:
            import platform
            if platform.system() == "Darwin":  # macOS
                network_interface = "en0"  # Standaard WiFi
            else:
                network_interface = "eth0"
        
        print(f"  📡 Netwerk interface: {network_interface}")
        
        robot = Go2RobotOfficial(
            ip_address=ip_address,
            network_interface=network_interface
        )
        
        # Test connect
        try:
            robot.connect()
            check_mark(True, "Verbinding succesvol via officiële SDK")
            
            # Test stand
            print("  ⏳ Test stand commando...")
            result = robot.stand()
            check_mark(True, "Stand commando verstuurd")
            time.sleep(1.0)
            
            # Test stop
            robot.stop()
            check_mark(True, "Stop commando verstuurd")
            
            robot.disconnect()
            return True
            
        except Exception as e:
            check_mark(False, f"Fout: {e}")
            print(f"  💡 Tip: Check netwerk interface naam (gebruik: --interface)")
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
    print("\nDit script test of alles correct is geïnstalleerd en geconfigureerd.")
    print("Gebruik dit script wanneer je de robot voor het eerst aanzet.\n")
    
    # Test 1: Imports
    imports_ok = test_imports()
    
    # Test 2: CycloneDDS
    cyclonedds_ok = test_cyclonedds()
    
    # Test 3: Netwerk verbinding
    network_ok = test_network_connection(args.ip)
    
    # Test 4: Custom wrapper (als netwerk OK)
    custom_wrapper_ok = False
    if network_ok and not args.skip_robot:
        print("\n⚠️  Let op: Robot tests zullen commando's naar de robot sturen!")
        print("Zorg dat de robot aan is en er voldoende ruimte is.")
        try:
            response = input("\nDoorgaan met robot tests? (y/n): ")
            if response.lower() == 'y':
                custom_wrapper_ok = test_custom_wrapper(args.ip)
            else:
                print("  ⏭️  Robot tests overgeslagen")
        except KeyboardInterrupt:
            print("\n  ⏭️  Robot tests overgeslagen")
    elif args.skip_robot:
        print("\n  ⏭️  Robot tests overgeslagen (--skip-robot flag)")
    
    # Test 5: Officiële SDK (als CycloneDDS OK en netwerk OK)
    official_sdk_ok = False
    if cyclonedds_ok and network_ok and not args.skip_robot:
        try:
            response = input("\nTest officiële SDK? (y/n): ")
            if response.lower() == 'y':
                official_sdk_ok = test_official_sdk(args.ip, args.interface)
            else:
                print("  ⏭️  Officiële SDK test overgeslagen")
        except KeyboardInterrupt:
            print("\n  ⏭️  Officiële SDK test overgeslagen")
    elif args.skip_robot:
        print("\n  ⏭️  Officiële SDK test overgeslagen (--skip-robot flag)")
    
    # Samenvatting
    print_header("Test Samenvatting")
    
    print("\n📋 Resultaten:")
    print(f"  {'✓' if imports_ok else '❌'} Imports: {'OK' if imports_ok else 'FAAL'}")
    print(f"  {'✓' if cyclonedds_ok else '❌'} CycloneDDS: {'OK' if cyclonedds_ok else 'FAAL'}")
    print(f"  {'✓' if network_ok else '❌'} Netwerk: {'OK' if network_ok else 'FAAL'}")
    if not args.skip_robot:
        print(f"  {'✓' if custom_wrapper_ok else '❌'} Custom Wrapper: {'OK' if custom_wrapper_ok else 'FAAL'}")
        print(f"  {'✓' if official_sdk_ok else '❌'} Officiële SDK: {'OK' if official_sdk_ok else 'FAAL'}")
    
    # Aanbevelingen
    print("\n💡 Aanbevelingen:")
    
    if not imports_ok:
        print("  - Check of alle dependencies geïnstalleerd zijn")
        print("  - Run: pip install -r requirements.txt")
    
    if not cyclonedds_ok:
        print("  - Installeer CycloneDDS: ./install_cyclonedds_macos.sh")
        print("  - Of export CYCLONEDDS_HOME handmatig")
    
    if not network_ok:
        print("  - Check of robot aan is")
        print("  - Check IP adres (standaard: 192.168.123.161)")
        print("  - Check netwerk verbinding")
        print("  - Check firewall instellingen")
    
    if not custom_wrapper_ok and network_ok:
        print("  - Robot accepteert mogelijk geen commando's")
        print("  - Check of robot EDU variant is")
        print("  - Check ontwikkelaarsmodus")
    
    if not official_sdk_ok and cyclonedds_ok and network_ok:
        print("  - Check netwerk interface naam")
        print("  - Probeer: --interface en0 (macOS) of eth0 (Linux)")
        print("  - Check DDS communicatie")
    
    # Eindresultaat
    all_tests = [imports_ok, cyclonedds_ok, network_ok]
    if not args.skip_robot:
        all_tests.extend([custom_wrapper_ok, official_sdk_ok])
    
    if all(all_tests):
        print("\n" + "=" * 70)
        print("  ✅ ALLE TESTS GESLAAGD!")
        print("=" * 70)
        print("\nJe kunt nu beginnen met de robot!")
        return 0
    else:
        print("\n" + "=" * 70)
        print("  ⚠️  SOMIGE TESTS MISLUKT")
        print("=" * 70)
        print("\nLos de bovenstaande problemen op voordat je verder gaat.")
        return 1

if __name__ == "__main__":
    exit(main())

