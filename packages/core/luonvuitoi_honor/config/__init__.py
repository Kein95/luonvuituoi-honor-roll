"""Config layer: Pydantic models + JSON loader for ``honor.config.json``."""

from luonvuitoi_honor.config.loader import ConfigError, load_config, load_config_dict
from luonvuitoi_honor.config.models import HonorConfig

__all__ = ["HonorConfig", "ConfigError", "load_config", "load_config_dict"]
