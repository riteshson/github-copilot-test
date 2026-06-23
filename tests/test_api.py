"""
Tests for the Mergington High School FastAPI backend.
Uses Arrange-Act-Assert structure and isolates state between tests.
"""

import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Snapshot and restore the in-memory activities state per test."""
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all(client):
    # Arrange
    path = "/activities"

    # Act
    response = client.get(path)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_post_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "tester.signup@example.com"
    path = f"/activities/{quote(activity_name, safe='')}/signup"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count + 1


def test_post_duplicate_signup_does_not_create_duplicate(client):
    # Arrange
    activity_name = "Programming Class"
    email = "tester.duplicate@example.com"
    path = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    first_response = client.post(path, params={"email": email})
    second_response = client.post(path, params={"email": email})

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert activities[activity_name]["participants"].count(email) == 1


def test_delete_unregister_removes_participant(client):
    # Arrange
    activity_name = "Tennis Club"
    email = "tester.unregister@example.com"
    path = f"/activities/{quote(activity_name, safe='')}/signup"
    signup_response = client.post(path, params={"email": email})
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    # Act
    delete_response = client.delete(path, params={"email": email})

    # Assert
    assert delete_response.status_code == 200
    assert email not in activities[activity_name]["participants"]
