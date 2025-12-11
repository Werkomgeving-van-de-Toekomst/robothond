"""
Unitree Go2 EDU SDK Wrapper

Een Python wrapper voor de Unitree Go2 EDU robot API.
"""

from .robot import Go2Robot
from .exceptions import Go2ConnectionError, Go2CommandError
from .config import load_config
from .flow_executor import FlowExecutor, FlowAction, ActionType, create_welcome_flow

# Probeer web search te importeren
try:
    from .web_search import WebSearcher
    HAS_WEB_SEARCH = True
except ImportError:
    HAS_WEB_SEARCH = False
    WebSearcher = None

# Probeer officiële SDK wrapper te importeren
try:
    from .robot_official import Go2RobotOfficial
    HAS_OFFICIAL_SDK = True
except ImportError:
    HAS_OFFICIAL_SDK = False
    Go2RobotOfficial = None

__version__ = "0.1.0"
__all__ = [
    "Go2Robot",
    "Go2ConnectionError",
    "Go2CommandError",
    "load_config",
    "FlowExecutor",
    "FlowAction",
    "ActionType",
    "create_welcome_flow",
    "HAS_OFFICIAL_SDK",
]

if HAS_WEB_SEARCH:
    __all__.append("WebSearcher")

if HAS_OFFICIAL_SDK:
    __all__.append("Go2RobotOfficial")

