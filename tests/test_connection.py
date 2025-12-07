"""
Verbinding tests voor Unitree Go2 EDU

Test de basis verbindingsfunctionaliteit met de robot.
"""

import pytest
import time
from src.unitree_go2 import Go2Robot, Go2ConnectionError


class TestConnection:
    """Test verbinding met robot"""
    
    def test_robot_initialization(self):
        """Test dat robot correct wordt geïnitialiseerd"""
        robot = Go2Robot(ip_address="192.168.123.161")
        assert robot.ip_address == "192.168.123.161"
        assert robot.port == 8080
        assert robot.timeout == 5.0
        assert not robot.connected
    
    def test_connect_disconnect(self):
        """Test verbinden en loskoppelen"""
        robot = Go2Robot(ip_address="192.168.123.161")
        
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
        try:
            with Go2Robot(ip_address="192.168.123.161") as robot:
                assert robot.connected is True
                print("✓ Context manager werkt correct")
        except Go2ConnectionError as e:
            pytest.skip(f"Kon niet verbinden met robot: {e}")
    
    def test_reconnect(self):
        """Test meerdere keren verbinden"""
        robot = Go2Robot(ip_address="192.168.123.161")
        
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

