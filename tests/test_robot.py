"""
Unit tests voor Go2Robot klasse

Let op: Deze tests vereisen een verbonden robot of mock implementatie.
"""

import pytest
from src.unitree_go2 import Go2Robot, Go2ConnectionError


def test_robot_initialization():
    """Test robot initialisatie"""
    robot = Go2Robot(ip_address="192.168.123.161")
    assert robot.ip_address == "192.168.123.161"
    assert robot.port == 8080
    assert not robot.connected


def test_robot_context_manager():
    """Test robot als context manager"""
    robot = Go2Robot(ip_address="192.168.123.161")
    # Let op: Dit vereist een echte verbinding of mock
    # with robot:
    #     assert robot.connected
    pass


# Meer tests kunnen hier worden toegevoegd

