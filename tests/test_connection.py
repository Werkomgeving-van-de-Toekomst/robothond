"""
Verbinding tests voor Unitree Go2 EDU

Test de basis verbindingsfunctionaliteit met de robot.
Gebruikt de officiële SDK.
"""

import pytest
import time
import os
import platform
from src.unitree_go2 import Go2Robot, Go2ConnectionError, HAS_OFFICIAL_SDK


# Skip alle tests als officiële SDK niet beschikbaar is
pytestmark = pytest.mark.skipif(
    not HAS_OFFICIAL_SDK,
    reason="Officiële SDK niet beschikbaar - installeer CycloneDDS"
)


def get_test_config():
    """Haal test configuratie op"""
    return {
        'ip_address': os.getenv('GO2_ROBOT_IP', '192.168.123.161'),
        'network_interface': os.getenv('GO2_NETWORK_INTERFACE', 
                                       'en0' if platform.system() == 'Darwin' else 'eth0')
    }


class TestConnection:
    """Test verbinding met robot"""
    
    def test_robot_initialization(self):
        """Test dat robot correct wordt geïnitialiseerd"""
        config = get_test_config()
        robot = Go2Robot(
            ip_address=config['ip_address'],
            network_interface=config['network_interface']
        )
        assert robot.ip_address == config['ip_address']
        assert robot.timeout == 5.0
        assert not robot.connected
    
    def test_connect_disconnect(self):
        """Test verbinden en loskoppelen"""
        config = get_test_config()
        robot = Go2Robot(
            ip_address=config['ip_address'],
            network_interface=config['network_interface']
        )
        
        # Test verbinden
        try:
            result = robot.connect()
            assert result is True
            assert robot.connected is True
            print("✓ Verbinding succesvol")
        except Go2ConnectionError as e:
            pytest.skip(f"Kon niet verbinden met robot: {e}")
        
        # Test loskoppelen
        robot.disconnect()
        assert robot.connected is False
        print("✓ Loskoppelen succesvol")
    
    def test_context_manager(self):
        """Test robot als context manager"""
        config = get_test_config()
        try:
            with Go2Robot(
                ip_address=config['ip_address'],
                network_interface=config['network_interface']
            ) as robot:
                assert robot.connected is True
                print("✓ Context manager werkt correct")
        except Go2ConnectionError as e:
            pytest.skip(f"Kon niet verbinden met robot: {e}")
    
    def test_reconnect(self):
        """Test meerdere keren verbinden"""
        config = get_test_config()
        robot = Go2Robot(
            ip_address=config['ip_address'],
            network_interface=config['network_interface']
        )
        
        try:
            # Eerste verbinding
            robot.connect()
            assert robot.connected
            robot.disconnect()
            
            # Tweede verbinding
            robot.connect()
            assert robot.connected
            robot.disconnect()
            print("✓ Herverbinden werkt correct")
        except Go2ConnectionError as e:
            pytest.skip(f"Kon niet verbinden met robot: {e}")
