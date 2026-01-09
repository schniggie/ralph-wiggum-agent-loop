# PRD Service Documentation

A lightweight Flask webservice for safely managing `prd.json` files during long Ralph Wiggum agent runs.

## Problem Statement

During long agent runs (100+ iterations), agents can corrupt `prd.json` files when directly editing them. This webservice provides a safe REST API interface using curl on localhost, eliminating direct file manipulation.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the Service

```bash
# Using default prd.json in current directory
python3 prd_service.py

# Using custom PRD file
PRD_FILE=/path/to/custom-prd.json python3 prd_service.py

# Using custom port
PORT=8080 python3 prd_service.py
```

The service runs on `http://127.0.0.1:5000` by default.

### Running in Background

```bash
# Start service in background
python3 prd_service.py &

# Stop service
pkill -f prd_service.py
```

## API Endpoints

### 1. Get All Tasks

Retrieve the complete PRD JSON blob.

```bash
curl http://localhost:5000/tasks
```

**Response:**
```json
[
  {
    "category": "feature",
    "description": "Set up project foundation",
    "steps": ["step1", "step2"],
    "passes": true
  },
  {
    "category": "bug",
    "description": "Fix authentication issue",
    "steps": ["step1", "step2"],
    "passes": false
  }
]
```

### 2. Search Tasks by Description

Search for tasks containing a specific term in their description (case-insensitive).

```bash
curl "http://localhost:5000/tasks/search?q=authentication"
```

**Response:**
```json
[
  {
    "index": 1,
    "task": {
      "category": "bug",
      "description": "Fix authentication issue",
      "steps": ["step1", "step2"],
      "passes": false
    }
  }
]
```

### 3. Get Specific Task

Retrieve a single task by its index (0-based).

```bash
curl http://localhost:5000/tasks/0
```

**Response:**
```json
{
  "index": 0,
  "task": {
    "category": "feature",
    "description": "Set up project foundation",
    "steps": ["step1", "step2"],
    "passes": true
  }
}
```

### 4. Mark Task as Passed

Update a task's `passes` field to `true`.

```bash
curl -X PATCH http://localhost:5000/tasks/1/pass
```

**Response:**
```json
{
  "success": true,
  "index": 1,
  "task": {
    "category": "bug",
    "description": "Fix authentication issue",
    "steps": ["step1", "step2"],
    "passes": true
  }
}
```

### 5. Health Check

Check if the service is running and the PRD file exists.

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "prd_file": "prd.json",
  "file_exists": true
}
```

## Error Responses

The API returns standard HTTP status codes:

- `400` - Bad Request (e.g., missing search query)
- `404` - Not Found (e.g., invalid task index)
- `500` - Internal Server Error (e.g., JSON parse error)

**Example Error:**
```json
{
  "error": "Not Found",
  "message": "Task index 99 not found"
}
```

## Usage in Agent Prompts

### Example: Get All Tasks
```bash
tasks=$(curl -s http://localhost:5000/tasks)
echo "$tasks" | jq .
```

### Example: Search for a Task
```bash
curl -s "http://localhost:5000/tasks/search?q=database" | jq .
```

### Example: Get Task by Index
```bash
task=$(curl -s http://localhost:5000/tasks/0)
echo "$task" | jq '.task.description'
```

### Example: Mark Task as Complete
```bash
# After completing task at index 2
curl -X PATCH http://localhost:5000/tasks/2/pass

# Verify it was updated
curl -s http://localhost:5000/tasks/2 | jq '.task.passes'
```

## Integration with Ralph Scripts

You can modify your `ralph_claude` or `ralph_kiro` scripts to start the service before the loop:

```bash
#!/bin/bash

# Start PRD service
python3 prd_service.py &
SERVICE_PID=$!

# Wait for service to start
sleep 2

# Run ralph loop
for i in $(seq 1 $MAX_ITERATIONS); do
    # Agent can now use curl to interact with prd.json
    # e.g., curl http://localhost:5000/tasks
    # ...
done

# Cleanup
kill $SERVICE_PID
```

## Configuration

The service can be configured via environment variables:

- `PRD_FILE` - Path to the PRD JSON file (default: `prd.json`)
- `PORT` - Port to run the service on (default: `5000`)

**Example:**
```bash
PRD_FILE=./plans/my-project-prd.json PORT=8080 python3 prd_service.py
```

## Benefits

1. **Safety**: No direct file editing prevents corruption
2. **Simplicity**: Standard REST API with curl commands
3. **Atomicity**: Each operation is a discrete HTTP request
4. **Debugging**: Easy to test and debug with curl
5. **Language Agnostic**: Works with any agent that can make HTTP requests

## File Permissions

The service needs:
- Read permission on the PRD file
- Write permission on the PRD file (for the `/pass` endpoint)
- Write permission in the directory (to update the file)

## Testing

```bash
# Start service
python3 prd_service.py &

# Test health endpoint
curl http://localhost:5000/health

# Test with example PRD
cp plans/example-prd.json prd.json

# Get all tasks
curl http://localhost:5000/tasks | jq .

# Search for tasks
curl "http://localhost:5000/tasks/search?q=authentication" | jq .

# Get specific task
curl http://localhost:5000/tasks/0 | jq .

# Mark task as passed
curl -X PATCH http://localhost:5000/tasks/0/pass | jq .

# Verify update
curl http://localhost:5000/tasks/0 | jq '.task.passes'

# Stop service
pkill -f prd_service.py
```

## Troubleshooting

**Service won't start:**
- Check if port 5000 is already in use: `lsof -i :5000`
- Try a different port: `PORT=8080 python3 prd_service.py`

**"File not found" errors:**
- Ensure `prd.json` exists in the current directory
- Or specify the path: `PRD_FILE=/path/to/prd.json python3 prd_service.py`

**"Invalid JSON" errors:**
- Validate your PRD file: `jq . prd.json`
- Check for syntax errors in the JSON

**Permission errors:**
- Ensure the file is writable: `chmod 644 prd.json`
- Check directory permissions: `ls -la`
