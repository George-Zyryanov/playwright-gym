"""
Base Page Object Model that provides common functionality for all pages.
"""
from typing import Any, Dict, List, Optional, Union

from playwright.sync_api import Page, Locator, expect

from config import settings
from utils.helpers import wait_for_navigation, take_screenshot


class BasePage:
    """Base class for all Page Objects."""
    
    def __init__(self, page: Page):
        """
        Initialize BasePage with a Playwright page.
        
        Args:
            page: Playwright page object
        """
        self.page = page
        self.timeout = settings.DEFAULT_TIMEOUT
        self.url = settings.BASE_URL
    
    def navigate(self, path: str = "") -> None:
        """
        Navigate to a URL.
        
        Args:
            path: Path to navigate to (appended to base URL)
        """
        full_url = f"{self.url}/{path.lstrip('/')}" if path else self.url
        self.page.goto(full_url, timeout=self.timeout)
        wait_for_navigation(self.page)
    
    def get_by_test_id(self, test_id: str) -> Locator:
        """
        Get element by data-testid attribute.
        
        Args:
            test_id: Test ID of the element
            
        Returns:
            Playwright Locator object
        """
        return self.page.locator(f"[data-testid='{test_id}']")
    
    def get_element(self, selector: str) -> Locator:
        """
        Get element by CSS selector.
        
        Args:
            selector: CSS selector
            
        Returns:
            Playwright Locator object
        """
        return self.page.locator(selector)
    
    def click(self, selector: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """
        Click on an element.
        
        Args:
            selector: CSS selector or Locator object
            timeout: Custom timeout in milliseconds (optional)
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        locator.click(timeout=timeout)
    
    def type_text(self, selector: Union[str, Locator], text: str, timeout: Optional[int] = None) -> None:
        """
        Type text into an input element.
        
        Args:
            selector: CSS selector or Locator object
            text: Text to type
            timeout: Custom timeout in milliseconds (optional)
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        locator.fill(text, timeout=timeout)
    
    def get_text(self, selector: Union[str, Locator], timeout: Optional[int] = None) -> str:
        """
        Get text content of an element.
        
        Args:
            selector: CSS selector or Locator object
            timeout: Custom timeout in milliseconds (optional)
            
        Returns:
            Text content of the element
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        return locator.text_content(timeout=timeout) or ""
    
    def is_visible(self, selector: Union[str, Locator], timeout: Optional[int] = None) -> bool:
        """
        Check if an element is visible.
        
        Args:
            selector: CSS selector or Locator object
            timeout: Custom timeout in milliseconds (optional)
            
        Returns:
            True if the element is visible, False otherwise
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        return locator.is_visible(timeout=timeout)
    
    def wait_for_element(self, selector: Union[str, Locator], timeout: Optional[int] = None) -> Locator:
        """
        Wait for an element to be visible.
        
        Args:
            selector: CSS selector or Locator object
            timeout: Custom timeout in milliseconds (optional)
            
        Returns:
            Playwright Locator object
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        expect(locator).to_be_visible(timeout=timeout)
        return locator
    
    def wait_for_element_to_be_hidden(self, selector: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """
        Wait for an element to be hidden.
        
        Args:
            selector: CSS selector or Locator object
            timeout: Custom timeout in milliseconds (optional)
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        expect(locator).to_be_hidden(timeout=timeout)
    
    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> None:
        """
        Wait for URL to match the pattern.
        
        Args:
            url_pattern: URL pattern to wait for
            timeout: Custom timeout in milliseconds (optional)
        """
        timeout = timeout or self.timeout
        self.page.wait_for_url(url_pattern, timeout=timeout)
    
    def select_option(self, selector: Union[str, Locator], value: str, timeout: Optional[int] = None) -> None:
        """
        Select an option from a dropdown.
        
        Args:
            selector: CSS selector or Locator object
            value: Option value to select
            timeout: Custom timeout in milliseconds (optional)
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        locator.select_option(value, timeout=timeout)
    
    def take_screenshot(self, name: Optional[str] = None) -> str:
        """
        Take a screenshot.
        
        Args:
            name: Screenshot name (optional)
            
        Returns:
            Path to the saved screenshot
        """
        return take_screenshot(self.page, name)
    
    def get_all_texts(self, selector: Union[str, Locator]) -> List[str]:
        """
        Get text content of all matching elements.
        
        Args:
            selector: CSS selector or Locator object
            
        Returns:
            List of text content of all matching elements
        """
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        return [text or "" for text in locator.all_text_contents()]
    
    def get_attribute(self, selector: Union[str, Locator], attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        Get attribute value of an element.
        
        Args:
            selector: CSS selector or Locator object
            attribute: Attribute name
            timeout: Custom timeout in milliseconds (optional)
            
        Returns:
            Attribute value or None if not found
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        return locator.get_attribute(attribute, timeout=timeout)
    
    def wait_for_network_idle(self, timeout: Optional[int] = None) -> None:
        """
        Wait for network to be idle.
        
        Args:
            timeout: Custom timeout in milliseconds (optional)
        """
        timeout = timeout or settings.NAVIGATION_TIMEOUT
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        
    def is_element_enabled(self, selector: Union[str, Locator], timeout: Optional[int] = None) -> bool:
        """
        Check if an element is enabled.
        
        Args:
            selector: CSS selector or Locator object
            timeout: Custom timeout in milliseconds (optional)
            
        Returns:
            True if the element is enabled, False otherwise
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        return locator.is_enabled(timeout=timeout)
        
    def hover(self, selector: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """
        Hover over an element.
        
        Args:
            selector: CSS selector or Locator object
            timeout: Custom timeout in milliseconds (optional)
        """
        timeout = timeout or self.timeout
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        locator.hover(timeout=timeout)
        
    def get_count(self, selector: Union[str, Locator]) -> int:
        """
        Get count of matching elements.
        
        Args:
            selector: CSS selector or Locator object
            
        Returns:
            Number of matching elements
        """
        locator = selector if isinstance(selector, Locator) else self.page.locator(selector)
        return locator.count()
        
    def press_key(self, key: str) -> None:
        """
        Press a key.
        
        Args:
            key: Key to press (e.g., 'Enter', 'Escape')
        """
        self.page.keyboard.press(key) 