"""
Configuration settings for the test automation framework.
Environment variables can be set in a .env file or directly in the environment.
"""
import os
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base paths
ROOT_DIR = Path(__file__).parent.parent
TESTS_DIR = ROOT_DIR / "tests"
REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
DATA_DIR = ROOT_DIR / "tests" / "data"

# Create directories if they don't exist
REPORTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)


class Environment(str, Enum):
    """Supported test environments."""
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


class Browser(str, Enum):
    """Supported browsers."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


# Environment settings
CURRENT_ENV = Environment(os.getenv("TEST_ENV", Environment.DEV))

# URLs for different environments
BASE_URLS: Dict[Environment, str] = {
    Environment.DEV: os.getenv("DEV_URL", "https://dev-example.com"),
    Environment.STAGING: os.getenv("STAGING_URL", "https://staging-example.com"),
    Environment.PRODUCTION: os.getenv("PROD_URL", "https://example.com"),
}

# Current base URL based on environment
BASE_URL = BASE_URLS[CURRENT_ENV]

# Test user credentials
TEST_USERS: Dict[Environment, Dict[str, Dict[str, str]]] = {
    Environment.DEV: {
        "admin": {
            "email": os.getenv("DEV_ADMIN_EMAIL", "admin@example.com"),
            "password": os.getenv("DEV_ADMIN_PASSWORD", "admin123"),
        },
        "standard": {
            "email": os.getenv("DEV_USER_EMAIL", "user@example.com"),
            "password": os.getenv("DEV_USER_PASSWORD", "user123"),
        },
    },
    Environment.STAGING: {
        "admin": {
            "email": os.getenv("STAGING_ADMIN_EMAIL", "admin@example.com"),
            "password": os.getenv("STAGING_ADMIN_PASSWORD", "admin123"),
        },
        "standard": {
            "email": os.getenv("STAGING_USER_EMAIL", "user@example.com"),
            "password": os.getenv("STAGING_USER_PASSWORD", "user123"),
        },
    },
    Environment.PRODUCTION: {
        "admin": {
            "email": os.getenv("PROD_ADMIN_EMAIL", "admin@example.com"),
            "password": os.getenv("PROD_ADMIN_PASSWORD", "admin123"),
        },
        "standard": {
            "email": os.getenv("PROD_USER_EMAIL", "user@example.com"),
            "password": os.getenv("PROD_USER_PASSWORD", "user123"),
        },
    },
}

# Timeout settings (in milliseconds)
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))

# Browser settings
DEFAULT_BROWSER = Browser(os.getenv("DEFAULT_BROWSER", Browser.CHROMIUM))
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))
VIEWPORT_SIZE = {
    "width": int(os.getenv("VIEWPORT_WIDTH", "1280")),
    "height": int(os.getenv("VIEWPORT_HEIGHT", "720")),
}

# Test execution settings
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "2"))
PARALLEL_WORKERS = int(os.getenv("PARALLEL_WORKERS", "4"))

# API settings
API_BASE_URL = os.getenv("API_BASE_URL", f"{BASE_URL}/api")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10000"))

# Reporting settings
ALLURE_RESULTS_DIR = os.getenv("ALLURE_RESULTS_DIR", "allure-results")


def get_browser_options(browser_name: Browser) -> Dict[str, Any]:
    """Get browser-specific options."""
    common_options = {
        "headless": HEADLESS,
        "slow_mo": SLOW_MO,
        "viewport": VIEWPORT_SIZE,
    }
    
    browser_specific: Dict[Browser, Dict[str, Any]] = {
        Browser.CHROMIUM: {
            "args": ["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
        },
        Browser.FIREFOX: {},
        Browser.WEBKIT: {},
    }
    
    return {**common_options, **browser_specific.get(browser_name, {})}


def get_env_config() -> Dict[str, Any]:
    """Get current environment configuration."""
    return {
        "environment": CURRENT_ENV,
        "base_url": BASE_URL,
        "users": TEST_USERS[CURRENT_ENV],
        "timeout": DEFAULT_TIMEOUT,
        "browser": DEFAULT_BROWSER,
        "headless": HEADLESS,
    }


def get_user_credentials(user_type: str) -> Dict[str, str]:
    """Get user credentials for the current environment."""
    return TEST_USERS[CURRENT_ENV].get(user_type, {}) 