# FastAPI Tests for Mergington High School Activities API

Integration tests for the activities management API using pytest and FastAPI's TestClient.

## Test Structure

- **`conftest.py`** - Pytest fixtures that provide:
  - Fresh FastAPI app instance with in-memory activities database for each test
  - TestClient for making HTTP requests to the API
  
- **`test_api.py`** - Integration tests organized by endpoint:
  - **TestGetActivitiesEndpoint** (3 tests) - GET /activities
  - **TestSignupEndpoint** (5 tests) - POST /activities/{activity_name}/signup
  - **TestDeleteParticipantEndpoint** (4 tests) - DELETE /activities/{activity_name}/participant
  - **TestRootEndpoint** (2 tests) - GET /
  - **TestStateAndIntegration** (3 tests) - State management and workflows

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run specific test class
```bash
pytest tests/test_api.py::TestGetActivitiesEndpoint -v
```

### Run specific test
```bash
pytest tests/test_api.py::TestSignupEndpoint::test_signup_valid_activity_and_email -v
```

### Run with coverage report
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Run tests and stop on first failure
```bash
pytest tests/ -x
```

## Test Coverage

**Total: 17 integration tests**

### GET /activities (3 tests)
- ✓ Returns all 3 activities with correct structure
- ✓ Each activity has required fields (description, schedule, max_participants, participants)
- ✓ Participant lists are correctly populated

### POST /activities/{activity_name}/signup (5 tests)
- ✓ Happy path: successful signup adds participant
- ✓ 404 when activity not found
- ✓ Duplicate participants allowed (current behavior)
- ✓ Same email can signup for multiple activities
- ✓ Email with special characters accepted

### DELETE /activities/{activity_name}/participant (4 tests)
- ✓ Happy path: successful participant removal
- ✓ 404 when participant not in activity
- ✓ 404 when activity not found
- ✓ Removes only one instance when duplicates exist

### GET / (2 tests)
- ✓ Root endpoint redirects to /static/index.html
- ✓ Redirect can be followed

### State & Integration (3 tests)
- ✓ Each test gets fresh, isolated state
- ✓ Signup immediately updates activities data (refresh workflow)
- ✓ Complete lifecycle: signup → verify → remove → verify

## Key Features

- **State Isolation** - Each test gets a fresh app instance via pytest fixture, preventing test pollution
- **No External Dependencies** - Tests use in-memory data, no database needed
- **Comprehensive** - Tests cover happy paths, error cases, and edge cases
- **Fast** - No async/await overhead, runs in milliseconds
- **Realistic** - Tests use actual API paths and HTTP methods as frontend uses them

## Test Data

Default activities (from conftest.py fixture):
- Chess Club (2 participants)
- Programming Class (2 participants)
- Gym Class (2 participants)

## Future Enhancements

After tests pass, consider:
1. Add Pydantic models for request/response validation
2. Add email format validation
3. Prevent duplicate participant signups
4. Add database persistence
5. Add authentication/authorization
6. Add CORS middleware
7. Add more edge case tests
