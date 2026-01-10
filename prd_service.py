#!/usr/bin/env python3
"""
PRD Service - A simple Flask webservice for managing prd.json files.

This service provides a REST API to interact with prd.json files safely,
preventing direct file editing which can lead to corruption during long
agent runs (100+ iterations).

Endpoints:
- GET /tasks - Retrieve full JSON blob
- GET /tasks/search?q=<query> - Search tasks by description
- GET /tasks/<index> - Get specific task by index
- PATCH /tasks/<index>/pass - Mark task as passed (sets passes: true)
"""

from flask import Flask, jsonify, request, abort
import json
import os
import fcntl
import logging
from typing import List, Dict, Any

app = Flask(__name__)

# Configuration
PRD_FILE = os.environ.get('PRD_FILE', 'prd.json')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_task(task: Any) -> bool:
    """
    Validate that a task has the expected structure.
    A task should be a dict with at least a 'description' field.
    """
    if not isinstance(task, dict):
        return False
    if 'description' not in task:
        return False
    return True


def validate_tasks_list(tasks: Any) -> bool:
    """Validate that tasks is a list of valid task objects."""
    if not isinstance(tasks, list):
        return False
    return all(validate_task(task) for task in tasks)


def read_prd() -> List[Dict[str, Any]]:
    """
    Read and parse the PRD JSON file with file locking for safe concurrent access.
    Returns an empty list if the file doesn't exist (creating it on first write).
    """
    if not os.path.exists(PRD_FILE):
        logger.warning(f"PRD file {PRD_FILE} does not exist, returning empty list")
        return []

    try:
        with open(PRD_FILE, 'r') as f:
            # Acquire shared lock for reading
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
                if not validate_tasks_list(data):
                    abort(500, description="PRD file does not contain a valid list of tasks")
                logger.info(f"Successfully read {len(data)} tasks from {PRD_FILE}")
                return data
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in PRD file: {str(e)}")
        abort(500, description=f"Invalid JSON in PRD file: {str(e)}")


def write_prd(tasks: List[Dict[str, Any]]) -> None:
    """
    Write tasks back to the PRD JSON file with file locking for safe concurrent access.
    Uses exclusive lock to prevent concurrent writes.
    """
    if not validate_tasks_list(tasks):
        abort(500, description="Cannot write invalid task list to PRD file")

    try:
        with open(PRD_FILE, 'w') as f:
            # Acquire exclusive lock for writing
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(tasks, f, indent=2)
                logger.info(f"Successfully wrote {len(tasks)} tasks to {PRD_FILE}")
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Failed to write PRD file: {str(e)}")
        abort(500, description=f"Failed to write PRD file: {str(e)}")


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Retrieve the full PRD JSON blob."""
    tasks = read_prd()
    return jsonify(tasks)


@app.route('/tasks/search', methods=['GET'])
def search_tasks():
    """
    Search tasks by description.
    Query parameter: q=<search_term>
    Returns tasks whose description contains the search term (case-insensitive).
    """
    query = request.args.get('q', '').lower()
    if not query:
        abort(400, description="Missing search query parameter 'q'")

    tasks = read_prd()
    results = []

    for idx, task in enumerate(tasks):
        description = task.get('description', '').lower()
        if query in description:
            results.append({
                'index': idx,
                'task': task
            })

    return jsonify(results)


@app.route('/tasks/<int:index>', methods=['GET'])
def get_task(index: int):
    """Get a specific task by its index."""
    tasks = read_prd()

    if index < 0 or index >= len(tasks):
        abort(404, description=f"Task index {index} not found")

    return jsonify({
        'index': index,
        'task': tasks[index]
    })


@app.route('/tasks/<int:index>/pass', methods=['PATCH'])
def mark_task_passed(index: int):
    """
    Mark a task as passed by setting passes: true.
    Uses atomic read-modify-write with file locking to prevent race conditions.
    """
    tasks = read_prd()

    if index < 0 or index >= len(tasks):
        logger.warning(f"Task index {index} not found (total tasks: {len(tasks)})")
        abort(404, description=f"Task index {index} not found")

    # Validate task structure before modifying
    if not validate_task(tasks[index]):
        abort(500, description=f"Task at index {index} has invalid structure")

    # Update the passes field
    old_value = tasks[index].get('passes', False)
    tasks[index]['passes'] = True
    write_prd(tasks)

    logger.info(f"Marked task {index} as passed (was: {old_value})")

    return jsonify({
        'success': True,
        'index': index,
        'task': tasks[index]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint with task statistics.
    Returns service status, file info, and task completion metrics.
    """
    file_exists = os.path.exists(PRD_FILE)
    response = {
        'status': 'healthy',
        'prd_file': PRD_FILE,
        'file_exists': file_exists
    }

    if file_exists:
        try:
            tasks = read_prd()
            total_tasks = len(tasks)
            passed_tasks = sum(1 for task in tasks if task.get('passes', False))
            completion_percentage = (passed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            response['statistics'] = {
                'total_tasks': total_tasks,
                'passed_tasks': passed_tasks,
                'pending_tasks': total_tasks - passed_tasks,
                'completion_percentage': round(completion_percentage, 2)
            }
        except Exception as e:
            logger.error(f"Error reading tasks for health check: {str(e)}")
            response['statistics_error'] = str(e)

    return jsonify(response)


@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad Request', 'message': str(e.description)}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not Found', 'message': str(e.description)}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal Server Error', 'message': str(e.description)}), 500


if __name__ == '__main__':
    # Default to localhost on port 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=False)
