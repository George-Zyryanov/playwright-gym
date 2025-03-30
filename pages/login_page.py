"""
Login Page Object Model.
"""
from typing import Dict, Optional

from playwright.sync_api import Page

from config import settings
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object for the login page."""
    
    def __init__(self, page: Page):
        """
        Initialize LoginPage with a Playwright page.
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = f"{settings.BASE_URL}/login"
        
        # Selectors
        self.email_input = "[data-testid='email-input']"
        self.password_input = "[data-testid='password-input']"
        self.login_button = "[data-testid='login-button']"
        self.remember_me_checkbox = "[data-testid='remember-me']"
        self.forgot_password_link = "[data-testid='forgot-password']"
        self.error_message = ".error-message"
        self.success_message = ".success-message"
        
    def navigate_to_login(self) -> None:
        """Navigate to the login page."""
        self.navigate()
        
    def login(self, email: str, password: str, remember_me: bool = False) -> None:
        """
        Login with the provided credentials.
        
        Args:
            email: User email
            password: User password
            remember_me: Whether to check the remember me checkbox (default: False)
        """
        self.type_text(self.email_input, email)
        self.type_text(self.password_input, password)
        
        if remember_me:
            self.click(self.remember_me_checkbox)
            
        self.click(self.login_button)
        self.wait_for_network_idle()
        
    def login_as_user(self, user_type: str = "standard") -> None:
        """
        Login as a predefined user type.
        
        Args:
            user_type: Type of user ("admin" or "standard", default: "standard")
        """
        credentials = settings.get_user_credentials(user_type)
        if not credentials:
            raise ValueError(f"No credentials found for user type: {user_type}")
            
        self.login(credentials["email"], credentials["password"])
        
    def forgot_password(self, email: str) -> None:
        """
        Initiate the forgot password flow.
        
        Args:
            email: User email
        """
        self.click(self.forgot_password_link)
        # Wait for forgot password form to appear
        self.wait_for_element("[data-testid='forgot-password-email']")
        self.type_text("[data-testid='forgot-password-email']", email)
        self.click("[data-testid='forgot-password-submit']")
        
    def get_error_message(self) -> str:
        """
        Get the error message displayed on the login page.
        
        Returns:
            Error message text
        """
        if self.is_visible(self.error_message):
            return self.get_text(self.error_message)
        return ""
        
    def get_success_message(self) -> str:
        """
        Get the success message displayed on the login page.
        
        Returns:
            Success message text
        """
        if self.is_visible(self.success_message):
            return self.get_text(self.success_message)
        return ""
        
    def is_logged_in(self) -> bool:
        """
        Check if the user is logged in.
        
        Returns:
            True if the user is logged in, False otherwise
        """
        # After successful login, we're redirected to the dashboard
        try:
            self.page.wait_for_url("**/dashboard", timeout=5000)
            return True
        except:
            return False
            
    def validate_login_form(self) -> Dict[str, bool]:
        """
        Validate that all login form elements are present.
        
        Returns:
            Dictionary indicating presence of each form element
        """
        return {
            "email_input": self.is_visible(self.email_input),
            "password_input": self.is_visible(self.password_input),
            "login_button": self.is_visible(self.login_button),
            "remember_me_checkbox": self.is_visible(self.remember_me_checkbox),
            "forgot_password_link": self.is_visible(self.forgot_password_link),
        } 