"""
Commando tests voor Unitree Go2 EDU

Test basis commando's zoals stand, sit, move, stop.
Gebruikt de officiële SDK.
"""

import pytest
import time
import os
import platform
from src.unitree_go2 import Go2Robot, Go2CommandError, Go2ConnectionError, HAS_OFFICIAL_SDK


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


class TestCommands:
    """Test basis commando's"""
    
    @pytest.fixture(scope="class")
    def robot(self):
        """Setup robot voor tests"""
        config = get_test_config()
        robot = Go2Robot(
            ip_address=config['ip_address'],
            network_interface=config['network_interface']
        )
        try:
            robot.connect()
            yield robot
            robot.disconnect()
        except Go2ConnectionError as e:
            pytest.skip(f"Kon niet verbinden met robot: {e}")
    
    def test_stand_command(self, robot):
        """Test stand commando"""
        try:
            result = robot.stand()
            print(f"✓ Stand commando: {result}")
            time.sleep(2)
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Stand commando mislukt: {e}")
    
    def test_sit_command(self, robot):
        """Test sit commando"""
        try:
            result = robot.sit()
            print(f"✓ Sit commando: {result}")
            time.sleep(2)
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Sit commando mislukt: {e}")
    
    def test_stop_command(self, robot):
        """Test stop commando"""
        try:
            result = robot.stop()
            print(f"✓ Stop commando: {result}")
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Stop commando mislukt: {e}")
    
    def test_move_forward(self, robot):
        """Test beweging vooruit"""
        try:
            robot.stand()
            time.sleep(1)
            
            result = robot.move(vx=0.2, vy=0.0, vyaw=0.0)
            print(f"✓ Beweging vooruit: {result}")
            time.sleep(2)
            
            robot.stop()
            time.sleep(1)
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Beweging vooruit mislukt: {e}")
    
    def test_move_backward(self, robot):
        """Test beweging achteruit"""
        try:
            robot.stand()
            time.sleep(1)
            
            result = robot.move(vx=-0.2, vy=0.0, vyaw=0.0)
            print(f"✓ Beweging achteruit: {result}")
            time.sleep(2)
            
            robot.stop()
            time.sleep(1)
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Beweging achteruit mislukt: {e}")
    
    def test_rotate(self, robot):
        """Test draaien"""
        try:
            robot.stand()
            time.sleep(1)
            
            result = robot.move(vx=0.0, vy=0.0, vyaw=0.3)
            print(f"✓ Draaien: {result}")
            time.sleep(2)
            
            robot.stop()
            time.sleep(1)
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Draaien mislukt: {e}")
