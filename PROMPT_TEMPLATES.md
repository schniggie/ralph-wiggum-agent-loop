# Ralph Wiggum Prompt Templates

This guide provides effective system and user prompts for implementing the Ralph Wiggum pattern with any LLM or coding agent.

## System Prompt Template (Universal)

Use this as your LLM's system message:

```
You are an autonomous software development agent. Your job is to complete tasks from a prioritized list (PRD - Product Requirements Document) by:

1. Reading the current PRD via the PRD service API
2. Reviewing git commit history to understand previous work
3. Identifying the highest-priority INCOMPLETE task
4. Following the steps for that task
5. Completing the implementation
6. Running quality checks (tests, type checking)
7. Updating the PRD via service API to mark the task as complete
8. Creating a detailed commit message with progress information
9. Repeating until all tasks are done

CRITICAL RULES:
- Only work on ONE task per iteration
- Always follow the steps exactly
- If a step fails, debug and fix it before moving on
- Use PRD service API for all PRD operations (NEVER directly edit prd.json)
- Track progress in git commit messages (detailed, structured format)
- Make atomic git commits with conventional commit format (feat:, fix:, etc.)
- When ALL tasks are complete, output exactly: <promise>COMPLETE</promise>
- NEVER skip quality checks or commit without passing tests

FILE HANDLING RULES (CRITICAL):
- PRD Service API: ONLY use the service API endpoints to read/update prd.json
- Git Commits: Document all progress in structured commit messages
- NEVER directly read or modify prd.json - always use curl to access the service
- Clean up any temporary files before committing
```

## User Prompt Template (Each Iteration)

```
Your instructions:
1. Use the PRD service API to fetch all tasks: curl -s http://localhost:5000/tasks
2. Review recent git commit history: git log --format="%h %s%n%b" -5
3. Identify the highest-priority task marked with "passes": false
4. Follow ALL the steps listed for that task
5. After implementing, run your project's quality checks:
   - npm test / pytest / go test (as applicable)
   - Type checking if available
6. Update the PRD using the service API:
   - Find the task index: curl -s "http://localhost:5000/tasks/search?q=task_description"
   - Mark as passed: curl -X PATCH http://localhost:5000/tasks/INDEX/pass
7. Create a detailed git commit with structured message (see format below)
8. Repeat: go back to step 1 until you encounter the <promise>COMPLETE</promise> marker

Git Commit Message Format:
<type>: <brief description>

Completed task #<index> from PRD: "<task description>"

Implementation details:
- <detail 1>
- <detail 2>

Testing:
- <test command>: <✓ passed | ✗ failed>

PRD Task: <index> (marked as passed)

If something fails:
- Debug the error
- Try to fix it
- If unfixable, document it in your commit message and move to the next task
- NEVER leave incomplete or broken code

Success Criteria:
- All tests pass
- No type errors
- Clean git commit history with detailed messages
- PRD fully updated via service API
```

## Prompt Tuning Tips

### For Your Specific Agent

1. **Understand the Agent**: Know what formats it expects (JSON, text, markdown)
2. **Be Explicit About Format**: Tell it exactly how to output responses
3. **Use Clear Markers**: Use `<promise>COMPLETE</promise>` or similar for state detection
4. **Give Context**: Include recent progress to help it understand what's been done
5. **Step-by-Step**: Break complex tasks into numbered substeps

### PRD Formatting

Keep PRD tasks:
- **Specific**: Not "implement auth" but "implement JWT token refresh logic"
- **Measurable**: Steps should be checkable
- **Small**: Complete in <30 minutes of code
- **Ordered**: Most important first
- **Atomic**: One feature per task

### Git Commit Message Format

Structure your commit messages for clear progress tracking:
- **Header**: Conventional commit format (feat:, fix:, etc.)
- **Task Reference**: Include PRD task index and description
- **Implementation Details**: List specific changes made
- **Testing Results**: Document test and type check status
- **PRD Update**: Confirm task marked as passed via API

## Backup and Safety

The Ralph Wiggum loop includes automatic backup functionality:

- Before each iteration, `prd.json` is automatically backed up to `../.backup/`
- Backup filenames include the iteration counter: `prd_iteration_1.json`, etc.
- Git commit history provides immutable backup of all progress
- The PRD service API prevents file corruption during concurrent operations
- If the agent corrupts prd.json, you can restore from the most recent backup

To implement this in your own loop script:

```bash
# At the start of each iteration
BACKUP_DIR="../.backup"
mkdir -p "$BACKUP_DIR"

if [ -f "prd.json" ]; then
    cp "prd.json" "$BACKUP_DIR/prd_iteration_${iteration_number}.json"
fi
```

## Common Issues & Solutions

### Agent Ignores PRD
- Make system prompt more forceful about following steps
- Add: "ONLY work on the exact task specified"
- Example task at top of PRD for reference

### Poor Code Quality
- Add explicit test/lint commands to each task's steps
- Include "verify code style matches project" as a step
- Make code review a mandatory step

### Incomplete Commits
- Add: "Create ONE atomic commit per task"
- Specify exact commit message format
- Include commit in the success criteria

### Infinite Loops
- Set iteration limit (50, 100, etc.)
- Add timeout to loop script
- Check for `<promise>COMPLETE</promise>` marker

### Agent Gets Stuck
- Make tasks smaller: Break into 2-3 more granular tasks
- Add examples: Include example code in the PRD
- Review git history: Check recent commits to understand what was attempted
- Verify API access: Ensure the PRD service is running and accessible
- Check output: Verify the agent is actually updating files
- Test manually: Do one task manually first to understand the setup
