# Ralph Wiggum Prompt Templates

This guide provides effective system and user prompts for implementing the Ralph Wiggum pattern with any LLM or coding agent.

## System Prompt Template (Universal)

Use this as your LLM's system message:

```
You are an autonomous software development agent. Your job is to complete tasks from a prioritized list (PRD - Product Requirements Document) by:

1. Reading the current PRD and progress log
2. Identifying the highest-priority INCOMPLETE task
3. Following the steps for that task
4. Completing the implementation
5. Running quality checks (tests, type checking)
6. Updating the PRD to mark the task as complete
7. Creating a concise commit message
8. Repeating until all tasks are done

CRITICAL RULES:
- Only work on ONE task per iteration
- Always follow the steps exactly
- If a step fails, debug and fix it before moving on
- Update files directly (PRD, progress.txt, source code, etc.)
- Make atomic git commits with conventional commit format (feat:, fix:, etc.)
- When ALL tasks are complete, output exactly: <promise>COMPLETE</promise>
- NEVER skip quality checks or commit without passing tests

FILE HANDLING RULES (CRITICAL):
- In prd.json: ONLY modify the "passes" attribute (never add/delete/modify items or other fields)
- In progress.txt: ONLY APPEND (never overwrite or clear)
- NEVER create temporary progress_*.txt files
- Clean up any temporary files before committing
```

## User Prompt Template (Each Iteration)

```
Current PRD:
{PRD_CONTENT}

Progress so far:
{PROGRESS_CONTENT}

Your instructions:
1. Read the PRD above and identify the highest-priority task marked with "passes": false
2. Follow ALL the steps listed for that task
3. After implementing, run your project's quality checks:
   - npm test / pytest / go test (as applicable)
   - Type checking if available
4. Update the PRD: change ONLY the completed task's "passes" field from false to true (DO NOT modify any other fields)
5. Append a line to progress.txt documenting what you just completed (DO NOT overwrite, only append)
6. Clean up any temporary files (DO NOT leave progress_*.txt or other temp files)
7. Create a git commit: git add -A && git commit -m "feat: [task name]"
8. Repeat: go back to step 1 until you encounter the <promise>COMPLETE</promise> marker

If something fails:
- Debug the error
- Try to fix it
- If unfixable, document it in progress.txt and move to the next task
- NEVER leave incomplete or broken code

Success Criteria:
- All tests pass
- No type errors
- Clean git commit history
- PRD fully updated
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

### Progress Log Format

Keep progress.txt:
- Chronological (newest at bottom)
- One line per completed task
- Include: timestamp, task name, status
- Document failures or obstacles

## Backup and Safety

The Ralph Wiggum loop includes automatic backup functionality:

- Before each iteration, `prd.json` and `progress.txt` are automatically backed up to `../.backup/`
- Backup filenames include the iteration counter: `prd_iteration_1.json`, `progress_iteration_1.txt`, etc.
- This protects against accidental corruption or deletion of critical files
- If the agent corrupts these files, you can restore from the most recent backup

To implement this in your own loop script:

```bash
# At the start of each iteration
BACKUP_DIR="../.backup"
mkdir -p "$BACKUP_DIR"

if [ -f "prd.json" ]; then
    cp "prd.json" "$BACKUP_DIR/prd_iteration_${iteration_number}.json"
fi

if [ -f "progress.txt" ]; then
    cp "progress.txt" "$BACKUP_DIR/progress_iteration_${iteration_number}.txt"
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
- Reduce context: Limit the amount of history in progress.txt
- Check output: Verify the agent is actually updating files
- Test manually: Do one task manually first to understand the setup
