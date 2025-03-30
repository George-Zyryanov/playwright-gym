"""
Helper utilities for test automation.
"""
import json
import random
import string
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from faker import Faker
from playwright.sync_api import Page, expect

from config import settings

# Initialize faker for generating test data
fake = Faker()


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email() -> str:
    """Generate a random email address."""
    return fake.email()


def generate_test_data() -> Dict[str, Any]:
    """Generate test data for form filling."""
    return {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'password': f"Test{fake.password(length=10)}123!",
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'zip_code': fake.zipcode(),
        'phone': fake.phone_number(),
    }


def take_screenshot(page: Page, name: Optional[str] = None) -> str:
    """
    Take a screenshot and save it to the screenshots directory.
    
    Args:
        page: Playwright page object
        name: Screenshot name (optional)
        
    Returns:
        Path to the saved screenshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_name = f"{name}_{timestamp}.png" if name else f"screenshot_{timestamp}.png"
    screenshots_dir = settings.SCREENSHOTS_DIR
    
    # Create directory if it doesn't exist
    screenshots_dir.mkdir(exist_ok=True, parents=True)
    
    screenshot_path = str(screenshots_dir / screenshot_name)
    page.screenshot(path=screenshot_path, full_page=True)
    return screenshot_path


def load_json_data(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary with the loaded data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_data(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path to the JSON file
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def wait_for_navigation(page: Page, timeout: Optional[int] = None) -> None:
    """
    Wait for navigation to complete with a custom timeout.
    
    Args:
        page: Playwright page object
        timeout: Custom timeout in milliseconds (optional)
    """
    timeout = timeout or settings.NAVIGATION_TIMEOUT
    page.wait_for_load_state("networkidle", timeout=timeout)


def retry(func, retries: int = 3, delay: int = 1, *args, **kwargs) -> Any:
    """
    Retry a function multiple times.
    
    Args:
        func: Function to retry
        retries: Number of retry attempts
        delay: Delay between retries in seconds
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        
    Returns:
        Result of the function call
    """
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(delay)


def expect_element_to_be_visible(page: Page, selector: str, timeout: Optional[int] = None) -> None:
    """
    Expect an element to be visible.
    
    Args:
        page: Playwright page object
        selector: Element selector
        timeout: Custom timeout in milliseconds (optional)
    """
    timeout = timeout or settings.DEFAULT_TIMEOUT
    element = page.locator(selector)
    expect(element).to_be_visible(timeout=timeout) 