"""
Unitree Go2 EDU SDK Wrapper

Een Python wrapper voor de Unitree Go2 EDU robot API.
"""

from .robot import Go2Robot
from .exceptions import Go2ConnectionError, Go2CommandError
from .config import load_config
from .flow_executor import FlowExecutor, FlowAction, ActionType, create_welcome_flow

__version__ = "0.1.0"
__all__ = [
    "Go2Robot",
    "Go2ConnectionError",
    "Go2CommandError",
    "load_config",
    "FlowExecutor",
    "FlowAction",
    "ActionType",
    "create_welcome_flow"
]

