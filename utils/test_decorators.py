"""Test decorators for metadata and traceability."""
import functools
import pytest
from typing import Optional, List, Dict, Any

def test_case(tc_id: str, description: Optional[str] = None, 
              priority: Optional[str] = None, 
              linked_issues: Optional[List[str]] = None) -> callable:
    """
    Decorator to link test with test case ID and metadata.
    
    Args:
        tc_id: Test case ID from test management system
        description: Optional description
        priority: Optional priority (P1, P2, etc.)
        linked_issues: Optional list of linked issues/requirements
    """
    def decorator(func):
        # Add the test case ID as a marker
        func = pytest.mark.tcid(tc_id)(func)
        
        # Add metadata for Allure reporting
        if pytest.importorskip("allure", reason="allure not installed"):
            import allure
            func = allure.id(tc_id)(func)
            func = allure.title(f"[{tc_id}] {description or func.__doc__}")(func)
            
            if priority:
                func = allure.severity(priority)(func)
            
            if linked_issues:
                for issue in linked_issues:
                    func = allure.issue(issue, f"Linked issue: {issue}")(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator 