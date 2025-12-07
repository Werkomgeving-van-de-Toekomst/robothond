"""
Commando tests voor Unitree Go2 EDU

Test basis commando's zoals stand, sit, move, stop.
"""

import pytest
import time
from src.unitree_go2 import Go2Robot, Go2CommandError, Go2ConnectionError


class TestCommands:
    """Test basis commando's"""
    
    @pytest.fixture(scope="class")
    def robot(self):
        """Setup robot voor tests"""
        robot = Go2Robot(ip_address="192.168.123.161")
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
            time.sleep(2)  # Wacht zodat robot kan reageren
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Stand commando mislukt: {e}")
    
    def test_sit_command(self, robot):
        """Test sit commando"""
        try:
            result = robot.sit()
            print(f"✓ Sit commando: {result}")
            time.sleep(2)  # Wacht zodat robot kan reageren
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
    
    def test_move_sideways(self, robot):
        """Test beweging zijwaarts"""
        try:
            robot.stand()
            time.sleep(1)
            
            result = robot.move(vx=0.0, vy=0.2, vyaw=0.0)
            print(f"✓ Beweging zijwaarts: {result}")
            time.sleep(2)
            
            robot.stop()
            time.sleep(1)
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Beweging zijwaarts mislukt: {e}")
    
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
    
    def test_combined_movement(self, robot):
        """Test gecombineerde beweging"""
        try:
            robot.stand()
            time.sleep(1)
            
            result = robot.move(vx=0.2, vy=0.1, vyaw=0.2)
            print(f"✓ Gecombineerde beweging: {result}")
            time.sleep(2)
            
            robot.stop()
            time.sleep(1)
            assert result is not None
        except Go2CommandError as e:
            pytest.fail(f"Gecombineerde beweging mislukt: {e}")

