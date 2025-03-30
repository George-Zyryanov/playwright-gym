"""
Example of data-driven tests using test data files.
"""
import csv
import json
import pytest
from pathlib import Path
from typing import Dict, Any, List

from playwright.sync_api import Page, expect

from config import settings
from pages.login_page import LoginPage


def load_user_data() -> Dict[str, Any]:
    """Load user data from JSON file."""
    file_path = settings.DATA_DIR / "test_users.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_login_scenarios() -> List[Dict[str, str]]:
    """Load login test scenarios from CSV file."""
    file_path = settings.DATA_DIR / "login_scenarios.csv"
    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.mark.ui
@pytest.mark.parametrize("user_type", ["standard", "admin", "premium"])
def test_login_with_valid_users(login_page: LoginPage, user_type: str):
    """Test login with different types of valid users from JSON data."""
    # Load user data
    user_data = load_user_data()["valid_users"][user_type]
    
    # Navigate to login page
    login_page.navigate_to_login()
    
    # Login with the user data
    login_page.login(user_data["email"], user_data["password"])
    
    # Verify successful login
    assert login_page.is_logged_in(), f"Login failed for {user_type} user"


@pytest.mark.ui
@pytest.mark.parametrize("user_type", ["wrong_password", "nonexistent", "locked_out"])
def test_login_with_invalid_users(login_page: LoginPage, user_type: str):
    """Test login with different types of invalid users from JSON data."""
    # Load user data
    user_data = load_user_data()["invalid_users"][user_type]
    
    # Navigate to login page
    login_page.navigate_to_login()
    
    # Login with the user data
    login_page.login(user_data["email"], user_data["password"])
    
    # Verify login failed
    assert not login_page.is_logged_in(), f"Login should have failed for {user_type} user"
    
    # Verify error message is displayed
    error_message = login_page.get_error_message()
    assert error_message, f"No error message displayed for {user_type} user"


@pytest.mark.ui
def test_login_with_csv_scenarios(login_page: LoginPage):
    """Test login with scenarios from CSV file."""
    # Load login scenarios
    scenarios = load_login_scenarios()
    
    for scenario in scenarios:
        # Navigate to login page
        login_page.navigate_to_login()
        
        # Login with scenario data
        login_page.login(scenario["email"], scenario["password"])
        
        # Verify result based on expected_result
        if scenario["expected_result"] == "success":
            assert login_page.is_logged_in(), \
                f"Login should have succeeded for email={scenario['email']}"
        else:
            assert not login_page.is_logged_in(), \
                f"Login should have failed for email={scenario['email']}"
            
            # Verify error message if specified
            if scenario["error_message"]:
                error_message = login_page.get_error_message()
                assert scenario["error_message"].lower() in error_message.lower(), \
                    f"Expected '{scenario['error_message']}' in error message, but got: '{error_message}'"


@pytest.mark.ui
def test_registration_form_with_test_data(page: Page):
    """Test filling a registration form with data from JSON file."""
    # Load registration form data
    form_data = load_user_data()["form_data"]["registration"]
    
    # Navigate to registration page (mock)
    page.goto("https://example.com/register")
    
    # This is a mock test since we don't have an actual registration page
    # In a real test, you would:
    # 1. Fill form fields with the form_data
    # 2. Submit the form
    # 3. Verify registration was successful
    
    # For demonstration purposes, we'll just log the data we would use
    print(f"Would register with: {json.dumps(form_data, indent=2)}") 