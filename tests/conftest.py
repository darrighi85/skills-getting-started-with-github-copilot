"""Shared fixtures for FastAPI test suite."""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src import app as app_module
from src.app import app


@pytest.fixture
def client():
    """
    Provide a TestClient for making requests to the FastAPI app.
    
    Arrange: Initialize the test client with the app instance.
    """
    return TestClient(app)


@pytest.fixture
def clean_activities(client):
    """
    Reset activities to their original state before each test.
    
    Arrange: Restore in-memory activities database to a clean state,
    preventing test interdependencies due to mutable global state.
    
    This ensures that:
    - Each test starts with 9 activities with their original participants
    - No signup/unregister from one test affects another test
    - The state is identical regardless of test execution order
    """
    # Store original state on first call
    if not hasattr(clean_activities, '_original_state'):
        clean_activities._original_state = deepcopy(app_module.activities)
    
    # Reset to original state before test
    app_module.activities.clear()
    app_module.activities.update(deepcopy(clean_activities._original_state))
    yield
    # Cleanup after test
    app_module.activities.clear()
    app_module.activities.update(deepcopy(clean_activities._original_state))
