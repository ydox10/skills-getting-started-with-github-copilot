"""
Pytest configuration and fixtures for API tests.
Provides TestClient and fresh app instances for each test.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os


@pytest.fixture
def app():
    """Create a fresh FastAPI app instance with in-memory activities for testing."""
    test_app = FastAPI()

    # In-memory activity database (same structure as main app)
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }

    # Define routes (same as main app)
    from fastapi.responses import RedirectResponse
    from fastapi import HTTPException

    @test_app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")

    @test_app.get("/activities")
    def get_activities():
        return activities

    @test_app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        activity = activities[activity_name]
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}

    @test_app.delete("/activities/{activity_name}/participant")
    def remove_participant(activity_name: str, email: str):
        """Remove a student from an activity"""
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        activity = activities[activity_name]
        if email in activity["participants"]:
            activity["participants"].remove(email)
            return {"message": f"Removed {email} from {activity_name}"}
        else:
            raise HTTPException(status_code=404, detail="Participant not found in this activity")

    return test_app


@pytest.fixture
def client(app):
    """Create a TestClient for the test app."""
    return TestClient(app)
