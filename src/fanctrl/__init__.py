"""Fan control package."""

__version__ = "1.0.1"

from .controller import FanController, load_config, get_cpu_temp, get_system_load, main

__all__ = [
    "FanController",
    "load_config",
    "get_cpu_temp",
    "get_system_load",
    "main",
    "__version__",
]
