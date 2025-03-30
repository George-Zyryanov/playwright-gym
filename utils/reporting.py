"""
Reporting utilities for test automation.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from playwright.sync_api import Page, TestInfo

from config import settings
from utils.helpers import take_screenshot


def attach_screenshot(page: Page, test_info: TestInfo, name: Optional[str] = None) -> str:
    """
    Take a screenshot and attach it to the test report.
    
    Args:
        page: Playwright page object
        test_info: Pytest test info object
        name: Screenshot name (optional)
        
    Returns:
        Path to the saved screenshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_name = f"{name or test_info.name}_{timestamp}.png"
    screenshot_path = str(settings.SCREENSHOTS_DIR / screenshot_name)
    
    # Take screenshot
    page.screenshot(path=screenshot_path, full_page=True)
    
    # Attach to test report
    test_info.attach(screenshot_name, screenshot_path, "image/png")
    
    return screenshot_path


def attach_logs(test_info: TestInfo, logs: Union[str, List[str], Dict[str, Any]]) -> None:
    """
    Attach logs to the test report.
    
    Args:
        test_info: Pytest test info object
        logs: Logs to attach (string, list of strings, or dictionary)
    """
    if isinstance(logs, dict):
        logs_content = json.dumps(logs, indent=2)
    elif isinstance(logs, list):
        logs_content = "\n".join(logs)
    else:
        logs_content = str(logs)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_name = f"{test_info.name}_logs_{timestamp}.txt"
    
    test_info.attach(log_name, logs_content, "text/plain")


def attach_network_logs(page: Page, test_info: TestInfo) -> None:
    """
    Attach network request/response logs to the test report.
    
    Args:
        page: Playwright page object
        test_info: Pytest test info object
    """
    requests = getattr(page, "_network_requests", [])
    if not requests:
        return
    
    network_logs = []
    for req in requests:
        try:
            response = req.response() if hasattr(req, "response") else None
            log_entry = {
                "url": req.url,
                "method": req.method,
                "status": response.status if response else None,
                "request_headers": req.headers if hasattr(req, "headers") else {},
                "response_headers": response.headers if response and hasattr(response, "headers") else {},
            }
            network_logs.append(log_entry)
        except Exception:
            # Skip if the request/response is no longer available
            pass
    
    if network_logs:
        attach_logs(test_info, {"network_requests": network_logs})


def create_allure_environment_properties() -> None:
    """
    Create environment.properties file for Allure reporting.
    """
    env_config = settings.get_env_config()
    
    properties = [
        f"Environment={env_config['environment']}",
        f"Browser={env_config['browser']}",
        f"Headless={env_config['headless']}",
        f"Base URL={env_config['base_url']}",
        f"Timeout={env_config['timeout']}",
        f"Viewport Width={settings.VIEWPORT_SIZE['width']}",
        f"Viewport Height={settings.VIEWPORT_SIZE['height']}",
        f"Python Version={os.environ.get('PYTHON_VERSION', 'Unknown')}",
        f"Playwright Version={os.environ.get('PLAYWRIGHT_VERSION', 'Unknown')}",
        f"Operating System={os.environ.get('OS', os.name)}",
    ]
    
    allure_dir = Path(settings.ALLURE_RESULTS_DIR)
    allure_dir.mkdir(exist_ok=True, parents=True)
    
    with open(allure_dir / "environment.properties", "w", encoding="utf-8") as f:
        f.write("\n".join(properties))


def save_test_artifacts(page: Page, test_info: TestInfo) -> None:
    """
    Save all test artifacts (screenshots, logs, etc.) when a test fails.
    
    Args:
        page: Playwright page object
        test_info: Pytest test info object
    """
    # Only save artifacts if the test failed
    if not test_info.failed:
        return
    
    try:
        # Take screenshot of the failure
        screenshot_path = take_screenshot(page, f"failure_{test_info.name}")
        test_info.attach("failure_screenshot", screenshot_path, "image/png")
        
        # Attach console logs
        console_logs = getattr(page, "_console_messages", [])
        if console_logs:
            attach_logs(test_info, {"console_logs": console_logs})
            
        # Attach network logs
        attach_network_logs(page, test_info)
            
        # Attach page HTML
        try:
            html_content = page.content()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_name = f"{test_info.name}_page_{timestamp}.html"
            test_info.attach(html_name, html_content, "text/html")
        except Exception:
            # Skip if unable to get page content
            pass
            
    except Exception as e:
        # If there's an error saving artifacts, log it but don't fail the test
        print(f"Error saving test artifacts: {str(e)}")


class TestLogCollector:
    """Collect logs during test execution."""
    
    def __init__(self):
        self.console_logs = []
        self.network_requests = []
        self.steps = []
        
    def add_console_log(self, log: str) -> None:
        """Add console log entry."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console_logs.append(f"[{timestamp}] {log}")
        
    def add_network_request(self, request_data: Dict[str, Any]) -> None:
        """Add network request data."""
        self.network_requests.append(request_data)
        
    def add_step(self, description: str) -> None:
        """Add test step."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.steps.append(f"[{timestamp}] {description}")
        
    def get_all_logs(self) -> Dict[str, Any]:
        """Get all collected logs."""
        return {
            "console_logs": self.console_logs,
            "network_requests": self.network_requests,
            "test_steps": self.steps,
            "timestamp": datetime.now().isoformat(),
        } 