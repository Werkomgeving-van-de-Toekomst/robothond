"""
Unitree Go2 EDU SDK

Python wrapper voor de Unitree Go2 EDU robot, gebaseerd op de officiële SDK.
"""

from .robot import Go2Robot, HAS_OFFICIAL_SDK
from .exceptions import Go2ConnectionError, Go2CommandError, Go2TimeoutError
from .config import load_config
from .flow_executor import FlowExecutor, FlowAction, ActionType, create_welcome_flow

# Probeer web search te importeren
try:
    from .web_search import WebSearcher
    HAS_WEB_SEARCH = True
except ImportError:
    HAS_WEB_SEARCH = False
    WebSearcher = None

# Backwards compatibility alias
Go2RobotOfficial = Go2Robot

__version__ = "0.2.0"
__all__ = [
    "Go2Robot",
    "Go2RobotOfficial",  # Backwards compatibility
    "Go2ConnectionError",
    "Go2CommandError",
    "Go2TimeoutError",
    "load_config",
    "FlowExecutor",
    "FlowAction",
    "ActionType",
    "create_welcome_flow",
    "HAS_OFFICIAL_SDK",
]

if HAS_WEB_SEARCH:
    __all__.append("WebSearcher")

