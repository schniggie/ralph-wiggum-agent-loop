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
from typing import List, Dict, Any

app = Flask(__name__)

# Configuration
PRD_FILE = os.environ.get('PRD_FILE', 'prd.json')


def read_prd() -> List[Dict[str, Any]]:
    """Read and parse the PRD JSON file."""
    try:
        with open(PRD_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        abort(500, description=f"Invalid JSON in PRD file: {str(e)}")


def write_prd(tasks: List[Dict[str, Any]]) -> None:
    """Write tasks back to the PRD JSON file."""
    try:
        with open(PRD_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
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
    """Mark a task as passed by setting passes: true."""
    tasks = read_prd()

    if index < 0 or index >= len(tasks):
        abort(404, description=f"Task index {index} not found")

    # Update the passes field
    tasks[index]['passes'] = True
    write_prd(tasks)

    return jsonify({
        'success': True,
        'index': index,
        'task': tasks[index]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'prd_file': PRD_FILE,
        'file_exists': os.path.exists(PRD_FILE)
    })


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
