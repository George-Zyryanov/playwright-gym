"""
Pytest configuration and fixtures.
"""
import os
import pytest
from typing import Any, Dict, Generator, Optional

from playwright.sync_api import Browser as PlaywrightBrowser
from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright

from config import settings
from pages.login_page import LoginPage
from utils.reporting import (
    save_test_artifacts,
    create_allure_environment_properties,
    TestLogCollector,
)


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption(
        "--browser",
        action="store",
        default=settings.DEFAULT_BROWSER,
        help=f"Browser to run tests on (default: {settings.DEFAULT_BROWSER})",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=not settings.HEADLESS,
        help="Run tests in headed mode",
    )
    parser.addoption(
        "--slow-mo",
        action="store",
        default=settings.SLOW_MO,
        help="Slow down execution by specified milliseconds",
    )


@pytest.fixture(scope="session")
def browser_name(request) -> str:
    """Get the browser name from the command line option."""
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def headed(request) -> bool:
    """Get the headed mode from the command line option."""
    return request.config.getoption("--headed")


@pytest.fixture(scope="session")
def slow_mo(request) -> int:
    """Get the slow-mo value from the command line option."""
    return int(request.config.getoption("--slow-mo"))


@pytest.fixture(scope="session")
def browser_type(playwright: Playwright, browser_name: str) -> PlaywrightBrowser:
    """Get the browser type from Playwright."""
    if browser_name.lower() == "chromium":
        return playwright.chromium
    elif browser_name.lower() == "firefox":
        return playwright.firefox
    elif browser_name.lower() == "webkit":
        return playwright.webkit
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")


@pytest.fixture(scope="session")
def browser_context_args(headed: bool, slow_mo: int) -> Dict[str, Any]:
    """Get browser context arguments."""
    return {
        "ignore_https_errors": True,
        "viewport": settings.VIEWPORT_SIZE,
        "headless": not headed,
        "slow_mo": slow_mo,
        "record_video_dir": "videos/" if os.getenv("RECORD_VIDEO", "false").lower() == "true" else None,
    }


@pytest.fixture(scope="session")
def browser(browser_type: PlaywrightBrowser, browser_context_args: Dict[str, Any]) -> Generator[PlaywrightBrowser, None, None]:
    """Create a browser instance."""
    browser_instance = browser_type.launch(**browser_context_args)
    yield browser_instance
    browser_instance.close()


@pytest.fixture
def context(browser: PlaywrightBrowser, browser_context_args: Dict[str, Any]) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    context_instance = browser.new_context(**browser_context_args)
    yield context_instance
    context_instance.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page_instance = context.new_page()
    
    # Setup page event listeners for logging
    log_collector = TestLogCollector()
    
    # Track console messages
    page_instance._console_messages = []
    page_instance.on("console", lambda msg: log_collector.add_console_log(f"[{msg.type}] {msg.text}"))
    
    # Track network requests
    page_instance._network_requests = []
    page_instance.on("request", lambda request: page_instance._network_requests.append(request))
    
    # Set the log collector on the page for later access
    page_instance._log_collector = log_collector
    
    yield page_instance
    

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """Create a login page instance."""
    return LoginPage(page)


@pytest.fixture
def authenticated_page(login_page: LoginPage) -> Page:
    """Get an authenticated page."""
    login_page.navigate_to_login()
    login_page.login_as_user("standard")
    
    # Check if login was successful
    assert login_page.is_logged_in(), "Login failed"
    
    return login_page.page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Handle test reporting and save test artifacts when a test fails.
    
    This hook is called for each of the setup, call, and teardown phases of a test.
    """
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    
    # Set report attribute for each phase of the test
    setattr(item, f"rep_{rep.when}", rep)
    
    # Only handle failures after the test runs ("call" phase)
    if rep.when == "call" and rep.failed:
        # Get the page fixture if available
        page = None
        for fixture_name in item._fixtureinfo.name2fixturedefs:
            if fixture_name == "page" and hasattr(item, "funcargs") and "page" in item.funcargs:
                page = item.funcargs["page"]
                break
        
        # If we have a page, save artifacts
        if page:
            try:
                test_info = getattr(item, "_testinfo", None)
                if test_info:
                    save_test_artifacts(page, test_info)
            except Exception as e:
                print(f"Error saving test artifacts: {str(e)}")

    # Get test case ID if available
    test_id = None
    for marker in item.iter_markers(name="tcid"):
        test_id = marker.args[0]
        break
    
    # If we have a test ID and test has finished running
    if test_id and rep.when == "call":
        # You could add logic here to report results to your test management system
        if hasattr(item.config, "workerinput"):  # Running in xdist worker
            # Handle distributed test execution
            pass
        else:
            # Report directly
            status = "passed" if rep.passed else "failed"
            # You could call your test management API here


@pytest.fixture(scope="session", autouse=True)
def setup_allure_environment():
    """Set up Allure environment properties at the start of the test run."""
    create_allure_environment_properties()


@pytest.fixture
def login_as_admin(login_page: LoginPage) -> Page:
    """Login as an admin user."""
    login_page.navigate_to_login()
    login_page.login_as_user("admin")
    
    # Check if login was successful
    assert login_page.is_logged_in(), "Admin login failed"
    
    return login_page.page


@pytest.fixture
def login_as_standard_user(login_page: LoginPage) -> Page:
    """Login as a standard user."""
    login_page.navigate_to_login()
    login_page.login_as_user("standard")
    
    # Check if login was successful
    assert login_page.is_logged_in(), "Standard user login failed"
    
    return login_page.page


# Add a custom marker for test case IDs
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "tcid(id): mark test with test case ID for traceability"
    ) 