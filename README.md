# Ralph Wiggum Agent Loop

A universal, framework-agnostic implementation of the **Ralph Wiggum pattern** - a devilishly simple loop-based approach for autonomous coding agents. Works with **any LLM** or coding agent (Claude, GPT, Llama, Gemini, etc.), not just Claude Code.

Based on Matt Pocock's [Ralph Wiggum technique](https://ghuntley.com/ralph/).

## What is Ralph Wiggum?

Ralph Wiggum is a minimalist approach to autonomous software development that uses:

- **A simple for loop** instead of complex orchestration systems
- - **A prioritized task list (PRD)** defining work to be done
  - - **Iterative execution** where each loop:
    -   1. Selects the highest-priority incomplete task
        2.   2. Completes the task
             3.   3. Updates progress tracking
                  4.   4. Commits work
                       5.   5. Repeats until complete
                         
                            6. The pattern mimics how real engineers work: pick a task → complete it → commit it → repeat.
                         
                            7. ## Key Principles
                         
                            8. - **Simplicity**: A basic loop is all you need
                               - - **Feedback Loops**: Tests, type checking, and CI ensure code quality
                                 - - **Single Focus**: Only work on one task per iteration
                                   - - **Progress Tracking**: Document what was done for the next person/agent
                                     - - **Atomic Commits**: Each completed task gets its own commit
                                      
                                       - ## Getting Started
                                      
                                       - ### 1. Project Setup
                                      
                                       - Clone or initialize your project, then create the following structure:
                                      
                                       - ```
                                         your-project/
                                         ├── plans/
                                         │   └── prd.json          # Your task definitions
                                         ├── progress.txt          # Progress log
                                         ├── run-ralph.sh          # Main loop script
                                         └── (your existing code)
                                         ```

                                         ### 2. Define Your PRD (Product Requirements Document)

                                         Create `plans/prd.json` with task definitions:

                                         ```json
                                         [
                                           {
                                             "category": "feature",
                                             "description": "Brief task description",
                                             "steps": [
                                               "Step 1 to complete task",
                                               "Step 2 to complete task",
                                               "Step 3 to validate completion"
                                             ],
                                             "passes": false
                                           },
                                           {
                                             "category": "bug",
                                             "description": "Another task",
                                             "steps": [
                                               "Reproduce the issue",
                                               "Fix the root cause",
                                               "Verify fix works"
                                             ],
                                             "passes": false
                                           }
                                         ]
                                         ```

                                         ### 3. Use the Loop Scripts

                                         #### Generic Bash Implementation

                                         Create `run-ralph.sh`:

                                         ```bash
                                         #!/bin/bash
                                         set -e

                                         if [ -z "$1" ]; then
                                           echo "Usage: $0 <iterations>"
                                           exit 1
                                         fi

                                         for ((i=1; i<=$1; i++)); do
                                           echo "=== Iteration $i ==="

                                           # Call your AI agent here with the PRD and progress
                                           # Example using curl/API:
                                           result=$(curl -X POST https://your-api-endpoint \
                                             -H "Content-Type: application/json" \
                                             -d @- << EOF
                                         {
                                           "model": "your-model",
                                           "messages": [
                                             {
                                               "role": "system",
                                               "content": "You are an autonomous developer. Here is the current PRD and progress. Pick the highest priority incomplete task and complete it. Update the PRD marking tasks as complete when done."
                                             },
                                             {
                                               "role": "user",
                                               "content": "PRD: $(cat plans/prd.json)\n\nProgress:\n$(cat progress.txt)\n\nInstructions:\n1. Select the highest-priority incomplete task\n2. Complete the task following all steps\n3. Run tests and type checking (if applicable)\n4. Update the PRD with completion status\n5. Append your progress to progress.txt\n6. Make a git commit of your changes\n7. If all tasks are complete, output <promise>COMPLETE</promise>"
                                             }
                                           ]
                                         }
                                         EOF
                                           )

                                           echo "$result"

                                           # Check if work is complete
                                           if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then
                                             echo "All tasks complete!"
                                             break
                                           fi
                                         done
                                         ```

                                         #### Using Claude (via Anthropic API)

                                         See `examples/claude-implementation.sh` for a complete Claude-specific implementation.

                                         ### 4. Initialize Progress Tracking

                                         Create `progress.txt`:

                                         ```
                                         === Ralph Wiggum Progress Log ===
                                         Started: $(date)

                                         ## Iteration 1
                                         - Completed: [Task name]
                                         - Status: Working on...

                                         ```

                                         ## Folder Structure

                                         ```
                                         .
                                         ├── README.md                    # This file
                                         ├── LICENSE                      # MIT License
                                         ├── plans/
                                         │   ├── prd.json                # Main task list
                                         │   └── example-prd.json        # Example PRD structure
                                         ├── progress.txt                # Progress tracking log
                                         ├── scripts/
                                         │   ├── run-ralph.sh           # Generic loop implementation
                                         │   ├── claude-loop.sh         # Claude-specific implementation
                                         │   ├── setup-prd.sh           # Helper to initialize PRD
                                         │   └── prompt-templates.md    # Prompt engineering guidance
                                         └── examples/
                                             ├── typescript-project/     # TypeScript project example
                                             ├── python-project/         # Python project example
                                             └── generic-project/        # Language-agnostic example
                                         ```

                                         ## Advanced Usage

                                         ### Custom Agent Integration

                                         To integrate with your specific agent/API:

                                         1. Modify the curl request in `run-ralph.sh` to match your API
                                         2. 2. Update the system prompt to guide your agent correctly
                                            3. 3. Ensure the agent outputs `<promise>COMPLETE</promise>` when finished
                                               4. 4. Test with a small number of iterations first
                                                 
                                                  5. ### PRD Best Practices
                                                 
                                                  6. - **Be specific**: "Add authentication" vs "Implement OAuth2 with Google and GitHub"
                                                     - - **Define success criteria**: Each step should be measurable
                                                       - - **Prioritize**: Order tasks by importance
                                                         - - **Track progress**: Update the `passes` field as tasks complete
                                                           - - **Atomic tasks**: One feature per task, not a sprint's worth of work
                                                            
                                                             - ### Progress Tracking
                                                            
                                                             - The `progress.txt` file serves as context for the next iteration:
                                                            
                                                             - ```
                                                               ## Iteration 1
                                                               - Completed: Set up project structure
                                                               - Tests: npm test (passed)
                                                               - Commit: build: initial project setup

                                                               ## Iteration 2
                                                               - Completed: Implement user authentication
                                                               - Tests: npm test (passed)
                                                               - Commit: feat: add user authentication with JWT

                                                               ...
                                                               ```

                                                               ## Implementation Examples

                                                               ### 1. Minimal Implementation (5 min setup)

                                                               ```bash
                                                               # Just need: prd.json, progress.txt, and a script that calls your agent
                                                               bash scripts/run-ralph.sh 50
                                                               ```

                                                               ### 2. With Quality Gates

                                                               ```bash
                                                               #!/bin/bash
                                                               # Run tests before each iteration
                                                               npm test && python -m pytest
                                                               bash scripts/run-ralph.sh 50
                                                               ```

                                                               ### 3. With Notifications

                                                               ```bash
                                                               #!/bin/bash
                                                               bash scripts/run-ralph.sh 100
                                                               if [ $? -eq 0 ]; then
                                                                 echo "Ralph Wiggum completed all tasks!" | mail -s "Backlog finished" you@example.com
                                                               fi
                                                               ```

                                                               ## How to Write Good Prompts

                                                               See `scripts/prompt-templates.md` for detailed guidance on:

                                                               - System prompts that work with any agent
                                                               - - Context injection strategies
                                                                 - - Progress tracking format
                                                                   - - Output validation patterns
                                                                    
                                                                     - ## Troubleshooting
                                                                    
                                                                     - ### Agent Gets Stuck
                                                                     - 
                                                                     - Break tasks into smaller steps
                                                                     - - Provide more specific acceptance criteria
                                                                       - - Add examples in the PRD
                                                                         - - Reduce iteration count and debug manually
                                                                          
                                                                           - ### Progress Not Updating
                                                                          
                                                                           - - Ensure agent outputs valid JSON/markdown
                                                                             - - Check that progress.txt is writable
                                                                               - - Verify git is configured (for commits)
                                                                                
                                                                                 - ### Tests Failing
                                                                                
                                                                                 - - Run quality checks before Ralph starts
                                                                                   - - Include test failures in the progress context
                                                                                     - - Have agent fix tests as part of each task
                                                                                      
                                                                                       - ## Real-World Examples
                                                                                      
                                                                                       - Coming soon:
                                                                                      
                                                                                       - - TypeScript/React frontend project
                                                                                         - - Python FastAPI backend
                                                                                           - - Go microservice
                                                                                             - - Rust CLI tool
                                                                                              
                                                                                               - ## Contributing
                                                                                              
                                                                                               - Found improvements? Submit a PR!
                                                                                              
                                                                                               - Improvements could include:
                                                                                              
                                                                                               - - New language implementations (Python, Go, Node, etc.)
                                                                                                 - - Better prompts for specific agents
                                                                                                   - - Integration examples
                                                                                                     - - Documentation improvements
                                                                                                      
                                                                                                       - ## References
                                                                                                      
                                                                                                       - - [Original Ralph Wiggum article](https://ghuntley.com/ralph/)
                                                                                                         - - [Anthropic: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
                                                                                                           - - [Matt Pocock's YouTube: Ralph Wiggum Technique](https://www.youtube.com/watch?v=_IK18goX4X8)
                                                                                                            
                                                                                                             - ## License
                                                                                                            
                                                                                                             - MIT - See LICENSE file
                                                                                                            
                                                                                                             - ---
                                                                                                             
                                                                                                             **Ralph Wiggum**: *"I'm in danger!"* ⚠️ (But your code won't be - it'll be shipping while you sleep)
                                                                                                             
