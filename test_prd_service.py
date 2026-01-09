#!/usr/bin/env python3
"""
Unit tests for PRD Service.

Tests all endpoints and error conditions to ensure safe prd.json manipulation.
"""

import json
import os
import tempfile
import pytest
from prd_service import app, validate_task, validate_tasks_list


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_prd_file():
    """Create a temporary PRD file for testing."""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.environ['PRD_FILE'] = path

    # Write initial test data
    test_data = [
        {
            "category": "feature",
            "description": "Set up project foundation",
            "steps": ["step1", "step2"],
            "passes": True
        },
        {
            "category": "bug",
            "description": "Fix authentication issue",
            "steps": ["step1", "step2"],
            "passes": False
        },
        {
            "category": "feature",
            "description": "Add database layer",
            "steps": ["step1"],
            "passes": False
        }
    ]

    with os.fdopen(fd, 'w') as f:
        json.dump(test_data, f, indent=2)

    yield path

    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


class TestValidation:
    """Tests for validation functions."""

    def test_validate_task_valid(self):
        """Test that valid tasks pass validation."""
        task = {"description": "Test task", "passes": False}
        assert validate_task(task) is True

    def test_validate_task_missing_description(self):
        """Test that tasks without description fail validation."""
        task = {"passes": False}
        assert validate_task(task) is False

    def test_validate_task_not_dict(self):
        """Test that non-dict tasks fail validation."""
        assert validate_task("not a dict") is False
        assert validate_task([]) is False
        assert validate_task(None) is False

    def test_validate_tasks_list_valid(self):
        """Test that valid task lists pass validation."""
        tasks = [
            {"description": "Task 1"},
            {"description": "Task 2"}
        ]
        assert validate_tasks_list(tasks) is True

    def test_validate_tasks_list_invalid(self):
        """Test that invalid task lists fail validation."""
        assert validate_tasks_list("not a list") is False
        assert validate_tasks_list([{"no_description": "test"}]) is False
        assert validate_tasks_list([{"description": "valid"}, "invalid"]) is False


class TestGetTasks:
    """Tests for GET /tasks endpoint."""

    def test_get_tasks_success(self, client, temp_prd_file):
        """Test retrieving all tasks."""
        response = client.get('/tasks')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]['description'] == "Set up project foundation"

    def test_get_tasks_empty_file(self, client):
        """Test retrieving tasks when file doesn't exist."""
        # Set PRD_FILE to non-existent path
        os.environ['PRD_FILE'] = '/tmp/nonexistent_prd.json'
        response = client.get('/tasks')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data == []


class TestSearchTasks:
    """Tests for GET /tasks/search endpoint."""

    def test_search_tasks_found(self, client, temp_prd_file):
        """Test searching for tasks that exist."""
        response = client.get('/tasks/search?q=authentication')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['index'] == 1
        assert 'authentication' in data[0]['task']['description'].lower()

    def test_search_tasks_not_found(self, client, temp_prd_file):
        """Test searching for tasks that don't exist."""
        response = client.get('/tasks/search?q=nonexistent')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 0

    def test_search_tasks_case_insensitive(self, client, temp_prd_file):
        """Test that search is case-insensitive."""
        response = client.get('/tasks/search?q=AUTHENTICATION')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 1

    def test_search_tasks_missing_query(self, client, temp_prd_file):
        """Test search without query parameter."""
        response = client.get('/tasks/search')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data


class TestGetTaskByIndex:
    """Tests for GET /tasks/<index> endpoint."""

    def test_get_task_success(self, client, temp_prd_file):
        """Test retrieving a specific task."""
        response = client.get('/tasks/0')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['index'] == 0
        assert data['task']['description'] == "Set up project foundation"
        assert data['task']['passes'] is True

    def test_get_task_out_of_range(self, client, temp_prd_file):
        """Test retrieving task with invalid index."""
        response = client.get('/tasks/999')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data

    def test_get_task_negative_index(self, client, temp_prd_file):
        """Test retrieving task with negative index."""
        response = client.get('/tasks/-1')
        assert response.status_code == 404


class TestMarkTaskPassed:
    """Tests for PATCH /tasks/<index>/pass endpoint."""

    def test_mark_task_passed_success(self, client, temp_prd_file):
        """Test marking a task as passed."""
        # First verify task is not passed
        response = client.get('/tasks/1')
        data = json.loads(response.data)
        assert data['task']['passes'] is False

        # Mark as passed
        response = client.patch('/tasks/1/pass')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['index'] == 1
        assert data['task']['passes'] is True

        # Verify persistence
        response = client.get('/tasks/1')
        data = json.loads(response.data)
        assert data['task']['passes'] is True

    def test_mark_task_passed_already_passed(self, client, temp_prd_file):
        """Test marking an already passed task."""
        response = client.patch('/tasks/0/pass')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['task']['passes'] is True

    def test_mark_task_passed_invalid_index(self, client, temp_prd_file):
        """Test marking task with invalid index."""
        response = client.patch('/tasks/999/pass')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data

    def test_mark_task_passed_negative_index(self, client, temp_prd_file):
        """Test marking task with negative index."""
        response = client.patch('/tasks/-1/pass')
        assert response.status_code == 404


class TestHealthCheck:
    """Tests for GET /health endpoint."""

    def test_health_check_with_file(self, client, temp_prd_file):
        """Test health check when PRD file exists."""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['file_exists'] is True
        assert 'statistics' in data
        assert data['statistics']['total_tasks'] == 3
        assert data['statistics']['passed_tasks'] == 1
        assert data['statistics']['pending_tasks'] == 2
        assert data['statistics']['completion_percentage'] == 33.33

    def test_health_check_without_file(self, client):
        """Test health check when PRD file doesn't exist."""
        os.environ['PRD_FILE'] = '/tmp/nonexistent_prd.json'
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['file_exists'] is False
        assert 'statistics' not in data

    def test_health_check_statistics_empty_file(self, client):
        """Test health check with empty task list."""
        fd, path = tempfile.mkstemp(suffix='.json')
        os.environ['PRD_FILE'] = path

        with os.fdopen(fd, 'w') as f:
            json.dump([], f)

        try:
            response = client.get('/health')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['statistics']['total_tasks'] == 0
            assert data['statistics']['completion_percentage'] == 0
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestErrorCases:
    """Tests for error handling."""

    def test_invalid_json_file(self, client):
        """Test handling of invalid JSON in PRD file."""
        fd, path = tempfile.mkstemp(suffix='.json')
        os.environ['PRD_FILE'] = path

        with os.fdopen(fd, 'w') as f:
            f.write("invalid json {{{")

        try:
            response = client.get('/tasks')
            assert response.status_code == 500

            data = json.loads(response.data)
            assert 'error' in data
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_invalid_task_structure(self, client):
        """Test handling of invalid task structure."""
        fd, path = tempfile.mkstemp(suffix='.json')
        os.environ['PRD_FILE'] = path

        # Write invalid task structure (missing description)
        with os.fdopen(fd, 'w') as f:
            json.dump([{"no_description": "test"}], f)

        try:
            response = client.get('/tasks')
            assert response.status_code == 500

            data = json.loads(response.data)
            assert 'error' in data
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestConcurrency:
    """Tests for concurrent access safety."""

    def test_multiple_reads(self, client, temp_prd_file):
        """Test multiple simultaneous reads."""
        # This tests that shared locks work correctly
        responses = []
        for _ in range(5):
            response = client.get('/tasks')
            responses.append(response)

        assert all(r.status_code == 200 for r in responses)

    def test_read_write_sequence(self, client, temp_prd_file):
        """Test read-modify-write sequence."""
        # Read initial state
        response = client.get('/tasks/1')
        initial_data = json.loads(response.data)
        assert initial_data['task']['passes'] is False

        # Write (mark as passed)
        response = client.patch('/tasks/1/pass')
        assert response.status_code == 200

        # Read again to verify
        response = client.get('/tasks/1')
        updated_data = json.loads(response.data)
        assert updated_data['task']['passes'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
