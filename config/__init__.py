"""
Configuration module for test automation framework.
"""
from config.settings import (
    BASE_URL,
    DEFAULT_TIMEOUT,
    NAVIGATION_TIMEOUT,
    DEFAULT_BROWSER,
    HEADLESS,
    CURRENT_ENV,
    Environment,
    Browser,
    get_browser_options,
    get_env_config,
    get_user_credentials,
)

__all__ = [
    'BASE_URL',
    'DEFAULT_TIMEOUT',
    'NAVIGATION_TIMEOUT',
    'DEFAULT_BROWSER',
    'HEADLESS',
    'CURRENT_ENV',
    'Environment',
    'Browser',
    'get_browser_options',
    'get_env_config',
    'get_user_credentials',
] 