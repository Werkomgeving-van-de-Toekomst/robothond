"""
Sensor tests voor Unitree Go2 EDU

Test het lezen van sensor data van de robot.
"""

import pytest
import time
from src.unitree_go2 import Go2Robot, Go2ConnectionError


class TestSensors:
    """Test sensor functionaliteit"""
    
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
    
    def test_get_state(self, robot):
        """Test ophalen van robot status"""
        try:
            state = robot.get_state()
            print(f"✓ Robot status: {state}")
            assert state is not None
            assert isinstance(state, dict)
        except Exception as e:
            pytest.fail(f"Ophalen status mislukt: {e}")
    
    def test_multiple_state_reads(self, robot):
        """Test meerdere keren status lezen"""
        states = []
        try:
            for i in range(5):
                state = robot.get_state()
                states.append(state)
                print(f"✓ Status lezen {i+1}/5: {state}")
                time.sleep(0.5)
            
            assert len(states) == 5
            print(f"✓ Alle {len(states)} status reads succesvol")
        except Exception as e:
            pytest.fail(f"Meerdere status reads mislukt: {e}")
    
    def test_state_during_movement(self, robot):
        """Test status lezen tijdens beweging"""
        try:
            robot.stand()
            time.sleep(1)
            
            # Start beweging
            robot.move(vx=0.2, vy=0.0, vyaw=0.0)
            
            # Lees status tijdens beweging
            states = []
            for i in range(3):
                state = robot.get_state()
                states.append(state)
                print(f"✓ Status tijdens beweging {i+1}/3: {state}")
                time.sleep(0.5)
            
            robot.stop()
            time.sleep(1)
            
            assert len(states) == 3
            print("✓ Status lezen tijdens beweging succesvol")
        except Exception as e:
            pytest.fail(f"Status lezen tijdens beweging mislukt: {e}")

