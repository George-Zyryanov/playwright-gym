# Playwright Python Test Automation GYM

This repository contains a comprehensive boilerplate for test automation using Playwright with Python, implementing industry best practices.

## Features

- Page Object Model (POM) architecture
- Fixtures for test setup and teardown
- Parallel test execution
- Screenshots on test failure
- HTML test reports
- Cross-browser testing (Chrome, Firefox, Safari)
- Environment-based configuration
- GitHub Actions CI/CD integration
- Allure reporting
- Type hints for better code completion and validation

## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Getting Started

1. Clone this repository:
```bash
git clone <your-repo-url>
cd playwright-python-boilerplate
```

2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run tests in a specific browser:
```bash
pytest --browser chromium  # Options: chromium, firefox, webkit
```

### Run tests in headed mode:
```bash
pytest --headed
```

### Run tests with HTML report:
```bash
pytest --html=report.html
```

### Run tests with Allure reporting:
```bash
pytest --alluredir=./allure-results
allure serve ./allure-results
```

### Run tests in parallel:
```bash
pytest -n 3  # Run tests using 3 workers
```

## Project Structure

```
├── config/                   # Configuration files
│   ├── __init__.py
│   └── settings.py           # Environment settings
├── pages/                    # Page Object Models
│   ├── __init__.py
│   ├── base_page.py          # Base page with common methods
│   └── login_page.py         # Example login page
├── tests/                    # Test files
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_login.py         # Example test
│   └── test_navigation.py    # Example test
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── helpers.py            # Helper functions
│   └── reporting.py          # Custom reporting logic
├── .github/                  # GitHub configuration
│   └── workflows/            # GitHub Actions workflows
│       └── playwright.yml    # CI/CD pipeline configuration
├── .gitignore                # Git ignore file
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Best Practices Implemented

1. **Page Object Model**: Separates page interactions from test logic
2. **Explicit Waits**: Avoid flaky tests by properly waiting for elements
3. **Configuration Management**: Environment-specific settings
4. **Test Data Management**: External test data for better maintainability
5. **Proper Assertions**: Clear and descriptive test assertions
6. **Error Screenshots**: Automatic screenshots on test failures
7. **CI/CD Integration**: Continuous testing with GitHub Actions
8. **Reporting**: Comprehensive test reports with Allure
9. **Clean Code**: Type hints, documentation, and consistent formatting

## CI/CD Pipeline

The GitHub Actions workflow in `.github/workflows/playwright.yml` provides:

1. Automated testing on multiple browsers
2. Testing on different operating systems
3. Test reports generation
4. Failure notifications

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 