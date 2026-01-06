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
4. Update the PRD: change the completed task's "passes" field from false to true
5. Append a line to progress.txt documenting what you just completed
6. Create a git commit: git add -A && git commit -m "feat: [task name]"
7. Repeat: go back to step 1 until you encounter the <promise>COMPLETE</promise> marker

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

## Integration Examples

### Generic API Call (cURL)

```bash
result=$(curl -s -X POST https://your-api-endpoint \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "model": "your-model-name",
  "messages": [
    {
      "role": "system",
      "content": "$(cat PROMPT_TEMPLATES.md | sed -n '/^You are an autonomous/,/NEVER skip quality/p')"
    },
    {
      "role": "user",
      "content": "Current PRD:\n$(cat plans/prd.json)\n\nProgress so far:\n$(cat progress.txt)\n\nYour instructions: [follow the steps above]"
    }
  ]
}
EOF
)
```

### Claude via Anthropic SDK

```bash
#!/bin/bash

ITERATIONS=${1:-50}

for ((i=1; i<=$ITERATIONS; i++)); do
  echo "=== Iteration $i ==="

  result=$(cat << 'EOF' | anthropic generate
{
  "system": "You are an autonomous developer. Work through tasks in the PRD one at a time. Complete each task, run tests, commit, and update progress. Output <promise>COMPLETE</promise> when done.",
  "user_message": "PRD:\n$(cat plans/prd.json)\n\nProgress:\n$(cat progress.txt)\n\nComplete the next highest-priority task."
}
EOF
)

  echo "$result" >> progress.txt

  if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then
    break
  fi
done
```

### OpenAI API

```bash
#!/bin/bash

function call_openai() {
  local prompt="$1"
  curl -s https://api.openai.com/v1/chat/completions \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d @- << EOF
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are a helpful coding assistant..."},
    {"role": "user", "content": "$prompt"}
  ],
  "temperature": 0.3,
  "max_tokens": 2000
}
EOF
}

prd_content=$(cat plans/prd.json)
progress_content=$(cat progress.txt)

result=$(call_openai "PRD: $prd_content\n\nProgress: $progress_content\n\nComplete the next task...")
```

## Prompt Tuning Tips

### For Your Specific Agent

1. **Understand the Agent**: Know what formats it expects (JSON, text, markdown)
2. 2. **Be Explicit About Format**: Tell it exactly how to output responses
   3. 3. **Use Clear Markers**: Use `<promise>COMPLETE</promise>` or similar for state detection
      4. 4. **Give Context**: Include recent progress to help it understand what's been done
         5. 5. **Step-by-Step**: Break complex tasks into numbered substeps
           
            6. ### PRD Formatting
           
            7. Keep PRD tasks:
            8. - **Specific**: Not "implement auth" but "implement JWT token refresh logic"
               - - **Measurable**: Steps should be checkable
                 - - **Small**: Complete in <30 minutes of code
                   - - **Ordered**: Most important first
                     - - **Atomic**: One feature per task
                      
                       - ### Progress Log Format
                      
                       - Keep progress.txt:
                       - - Chronological (newest at bottom)
                         - - One line per completed task
                           - - Include: timestamp, task name, status
                             - - Document failures or obstacles
                              
                               - ## Debugging
                              
                               - If the agent gets stuck:
                              
                               - 1. **Make tasks smaller**: Break into 2-3 more granular tasks
                                 2. 2. **Add examples**: Include example code in the PRD
                                    3. 3. **Reduce context**: Limit the amount of history in progress.txt
                                       4. 4. **Check output**: Verify the agent is actually updating files
                                          5. 5. **Test manually**: Do one task manually first to understand the setup
                                            
                                             6. ## Common Issues & Solutions
                                            
                                             7. ### Agent Ignores PRD
                                             8. - Make system prompt more forceful about following steps
                                                - - Add: "ONLY work on the exact task specified"
                                                  - - Example task at top of PRD for reference
                                                   
                                                    - ### Poor Code Quality
                                                    - - Add explicit test/lint commands to each task's steps
                                                      - - Include "verify code style matches project" as a step
                                                        - - Make code review a mandatory step
                                                         
                                                          - ### Incomplete Commits
                                                          - - Add: "Create ONE atomic commit per task"
                                                            - - Specify exact commit message format
                                                              - - Include commit in the success criteria
                                                               
                                                                - ### Infinite Loops
                                                                - - Set iteration limit (50, 100, etc.)
                                                                  - - Add timeout to loop script
                                                                    - - Check for `<promise>COMPLETE</promise>` marker
                                                                      - 
