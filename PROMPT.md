# Ralph Wiggum Agent - Code Implementation Task

You are an expert software engineer working on a feature backlog. Your task is to:

1. **Read the PRD** using the PRD service API to understand all tasks
2. **Review recent progress** using `git log` to understand what's been completed
3. **Identify the highest-priority incomplete task**
4. **Implement ONLY that single feature completely**
5. **Ensure code quality**:
   - Run `pnpm typecheck` to verify type safety
   - Run `pnpm test` to ensure tests pass
6. **Commit your work** with a descriptive commit message that includes progress details

## Important Rules

- **ONE FEATURE AT A TIME**: Do not work on multiple features in one iteration
- **SMALL, COMPLETE CHANGES**: Your change should be deployable and tested
- **READ COMMIT HISTORY**: Use `git log` to understand what's been completed in previous iterations
- **UPDATE THE PRD**: Mark completed items as done using the PRD service
- **DOCUMENT IN COMMITS**: Include detailed progress information in your commit messages
- **Quality First**: Type checking and tests must pass
- **TDD APPROACH**: Write tests before implementation, ensure code runs from commit 1

## Test-Driven Development (TDD) Workflow

Follow this workflow for every feature to ensure working, runnable code:

1. **Start with e2e tests**: Before implementing a feature, write end-to-end tests that verify the feature works in a real environment
2. **Run tests first**: Execute tests to confirm they fail (red phase)
3. **Implement the feature**: Write minimal code to make tests pass (green phase)
4. **Verify with docker-compose**: If the project uses docker-compose for testing, run the full stack to validate the feature works end-to-end
5. **Refactor if needed**: Clean up code while keeping tests passing

### Running e2e Tests

If a `docker-compose.yml` or similar testing stack exists:
```bash
# Start the test environment
docker-compose up -d

# Run e2e tests against the stack
pnpm test:e2e  # or equivalent test command

# Stop the environment
docker-compose down
```

**Goal**: Every commit should produce runnable, working code. Avoid implementing features without tests, as this leads to manual debugging sessions later.

## PRD Service API Usage

**CRITICAL**: Never directly read or modify `prd.json`. Always use the PRD service via curl commands.

The PRD service runs on `http://localhost:5000` and provides these endpoints:

### Get All Tasks
```bash
curl -s http://localhost:5000/tasks
```
Returns the complete list of all tasks in the PRD.

### Search Tasks by Description
```bash
curl -s "http://localhost:5000/tasks/search?q=search_term"
```
Finds tasks containing the search term (case-insensitive). Use this to locate specific features.

### Get Specific Task
```bash
curl -s http://localhost:5000/tasks/INDEX
```
Retrieves a single task by its 0-based index. Returns task details with the index.

### Mark Task as Passed
```bash
curl -X PATCH http://localhost:5000/tasks/INDEX/pass
```
Marks a task at INDEX as complete (`passes: true`). This is the ONLY way to update task status.

### Check Service Health
```bash
curl -s http://localhost:5000/health
```
Verify the service is running and get task statistics (total, passed, pending, completion percentage).

### Example Workflow
```bash
# 1. Get all tasks and find the first incomplete one
tasks=$(curl -s http://localhost:5000/tasks)
echo "$tasks" | jq '.[] | select(.passes == false) | .description' | head -n 1

# 2. Find task index by searching
curl -s "http://localhost:5000/tasks/search?q=authentication" | jq '.[0].index'

# 3. Get task details
curl -s http://localhost:5000/tasks/0 | jq '.task'

# 4. After completing the implementation, mark task as passed
curl -X PATCH http://localhost:5000/tasks/0/pass

# 5. Verify update
curl -s http://localhost:5000/tasks/0 | jq '.task.passes'
```

## Critical File Handling Rules

### PRD Service Interaction
- **NEVER directly read or edit `prd.json`** - always use the PRD service API
- **ONLY use the `/pass` endpoint** to mark tasks complete
- **DO NOT attempt to modify task descriptions, steps, or categories** via the API
- The service ensures atomic operations and prevents file corruption during long agent runs

### Git Commit Message Format
Your commit messages should follow this structure to maintain clear progress tracking:

**Required format:**
```
<type>: <brief description>

Completed task #<index> from PRD: "<task description>"

Implementation details:
- <detail 1>
- <detail 2>
- <detail 3>

Testing:
- pnpm typecheck: <✓ passed | ✗ failed>
- pnpm test: <✓ passed | ✗ failed>
- e2e tests: <✓ passed | ✗ failed | ⊘ N/A>

PRD Task: <index> (marked as passed)
```

**Example:**
```
feat: implement user authentication with JWT

Completed task #2 from PRD: "Implement user authentication"

Implementation details:
- Added JWT library (jsonwebtoken)
- Created /auth/login endpoint with password validation
- Implemented token refresh mechanism
- Added auth middleware for protected routes

Testing:
- pnpm typecheck: ✓ passed
- pnpm test: ✓ all tests passing (auth.test.ts added)
- e2e tests: ✓ passed (docker-compose stack verified)

PRD Task: 2 (marked as passed)
```

**Notes:**
- You can commit intermediate progress during your work, but the final commit MUST include the full details above
- Use conventional commit types: `feat`, `fix`, `refactor`, `test`, `docs`, etc.
- Be specific in implementation details - this helps the next iteration understand context

### Reading Previous Progress
To understand what's been completed and get context from previous iterations:

**Get overview of recent work:**
```bash
git log --oneline -20
```
This shows the last 20 commits with one-line summaries.

**Get detailed view of recent tasks:**
```bash
git log --format="%h %s%n%b" -3
```
This shows the last 3 commits with full commit bodies, providing detailed context about recent implementations.

## When Complete

If you determine the PRD is fully complete, output `<promise>COMPLETE</promise>` to signal the loop to exit.

## Current State

Use `curl -s http://localhost:5000/tasks` to get the full feature list and `git log` to check what's been completed in previous iterations.
