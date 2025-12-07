"""
Error handling tests voor Unitree Go2 EDU

Test foutafhandeling en edge cases.
"""

import pytest
from src.unitree_go2 import Go2Robot, Go2ConnectionError, Go2CommandError


class TestErrorHandling:
    """Test error handling"""
    
    def test_command_without_connection(self):
        """Test commando zonder verbinding"""
        robot = Go2Robot(ip_address="192.168.123.161")
        
        with pytest.raises(Go2ConnectionError):
            robot.stand()
        print("✓ Foutmelding bij commando zonder verbinding werkt correct")
    
    def test_invalid_ip_address(self):
        """Test verbinding met ongeldig IP adres"""
        robot = Go2Robot(ip_address="192.168.999.999")
        
        # Dit zou moeten falen, maar niet crashen
        try:
            robot.connect()
            robot.disconnect()
        except Go2ConnectionError:
            print("✓ Foutmelding bij ongeldig IP adres werkt correct")
        except Exception as e:
            pytest.fail(f"Onverwachte fout: {e}")
    
    def test_disconnect_twice(self):
        """Test meerdere keren loskoppelen"""
        robot = Go2Robot(ip_address="192.168.123.161")
        
        try:
            robot.connect()
            robot.disconnect()
            robot.disconnect()  # Tweede keer zou geen fout moeten geven
            print("✓ Meerdere keren loskoppelen werkt correct")
        except Exception as e:
            pytest.fail(f"Meerdere keren loskoppelen gaf fout: {e}")
    
    def test_command_after_disconnect(self):
        """Test commando na loskoppelen"""
        robot = Go2Robot(ip_address="192.168.123.161")
        
        try:
            robot.connect()
            robot.disconnect()
            
            with pytest.raises(Go2ConnectionError):
                robot.stand()
            print("✓ Foutmelding bij commando na loskoppelen werkt correct")
        except Go2ConnectionError:
            pytest.skip("Kon niet verbinden met robot voor test")

