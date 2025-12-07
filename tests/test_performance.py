"""
Performance tests voor Unitree Go2 EDU

Test de performance en responsiviteit van de SDK.
"""

import pytest
import time
from src.unitree_go2 import Go2Robot, Go2ConnectionError


class TestPerformance:
    """Test performance"""
    
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
    
    def test_command_latency(self, robot):
        """Test latency van commando's"""
        latencies = []
        
        for i in range(10):
            start = time.time()
            robot.get_state()
            latency = time.time() - start
            latencies.append(latency)
            time.sleep(0.1)
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        print(f"✓ Gemiddelde latency: {avg_latency*1000:.2f}ms")
        print(f"✓ Minimale latency: {min_latency*1000:.2f}ms")
        print(f"✓ Maximale latency: {max_latency*1000:.2f}ms")
        
        assert avg_latency < 1.0  # Minder dan 1 seconde gemiddeld
        assert max_latency < 2.0   # Minder dan 2 seconden maximum
    
    def test_rapid_commands(self, robot):
        """Test snelle opeenvolgende commando's"""
        start = time.time()
        
        for i in range(20):
            robot.get_state()
        
        total_time = time.time() - start
        avg_time = total_time / 20
        
        print(f"✓ 20 commando's in {total_time:.2f} seconden")
        print(f"✓ Gemiddeld {avg_time*1000:.2f}ms per commando")
        
        assert total_time < 10.0  # Minder dan 10 seconden voor 20 commando's
    
    def test_connection_time(self, robot):
        """Test verbindingstijd"""
        times = []
        
        for i in range(5):
            robot.disconnect()
            start = time.time()
            robot.connect()
            connect_time = time.time() - start
            times.append(connect_time)
        
        avg_time = sum(times) / len(times)
        print(f"✓ Gemiddelde verbindingstijd: {avg_time*1000:.2f}ms")
        
        assert avg_time < 2.0  # Minder dan 2 seconden gemiddeld

