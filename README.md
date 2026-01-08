# Ralph Wiggum Agent Loop

A universal, framework-agnostic implementation of the **Ralph Wiggum pattern** - a simple loop-based approach for autonomous coding agents. Works with **any LLM** or coding agent (Claude, GPT, Llama, Gemini, etc.).

Based on Matt Pocock's [Ralph Wiggum technique](https://ghuntley.com/ralph/).

## What is Ralph Wiggum?

Ralph Wiggum is a minimalist approach to autonomous software development that uses:

- **A simple for loop** instead of complex orchestration systems
- **A prioritized task list (PRD)** defining work to be done
- **Iterative execution** where each loop:
  1. Selects the highest-priority incomplete task
  2. Completes the task
  3. Updates progress tracking
  4. Commits work
  5. Repeats until complete

The pattern mimics how real engineers work: pick a task → complete it → commit it → repeat.

## Key Principles

- **Simplicity**: A basic loop is all you need
- **Feedback Loops**: Tests, type checking, and CI ensure code quality
- **Single Focus**: Only work on one task per iteration
- **Progress Tracking**: Document what was done for the next person/agent
- **Atomic Commits**: Each completed task gets its own commit

## Project Structure

```
.
├── README.md              # This file
├── PROMPT.md              # Agent instructions
├── PRD-PROMPT.md          # Detailed PRD creation guide
├── PROMPT_TEMPLATES.md    # Prompt templates for other agents
├── progress.txt           # Progress log (example)
├── ralph_claude           # Claude implementation script
├── plans/
│   └── example-prd.json   # Example PRD file
└── LICENSE
```

## Quick Start

### 1. Create Your PRD

Create a `prd.json` file in your project root with your task list (see `plans/example-prd.json` for reference):

```json
[
  {
    "category": "feature",
    "description": "Implement user authentication",
    "steps": [
      "Create login endpoint",
      "Add JWT token generation",
      "Write tests"
    ],
    "passes": false
  }
]
```

### 2. Initialize Progress

Create a `progress.txt` file to track your work:

```
=== Ralph Wiggum Progress Log ===
Project: Your Project Name
Started: 2026-01-06
```

### 3. Run the Loop

For Claude Code CLI:

```bash
./ralph_claude 50  # Run 50 iterations
```

The script will:
- Read your PRD and progress
- Select the highest-priority task
- Implement it completely
- Run tests and type checks
- Commit the changes
- Update progress
- Repeat

For other AI agents (GPT, Gemini, etc.), see `PROMPT_TEMPLATES.md` for implementation guidance.

## How It Works

1. **Backup**: Before each iteration, `prd.json` and `progress.txt` are backed up to `../.backup/` with iteration counter in filename
2. **Loop starts**: Agent reads `prd.json` and `progress.txt`
3. **Task selection**: Agent picks highest-priority incomplete task
4. **Implementation**: Agent completes the task, runs tests, makes commit
5. **Progress update**: Agent updates `prd.json` (only the `passes` field) and appends to `progress.txt`
6. **Repeat**: Loop continues until all tasks complete or max iterations reached

### Safety Features

- **Automatic backups**: `prd.json` and `progress.txt` are backed up before each iteration to `../.backup/prd_iteration_N.json` and `../.backup/progress_iteration_N.txt`
- **Restricted modifications**: The agent can only change the `passes` attribute in `prd.json`, preventing accidental corruption
- **Append-only progress**: `progress.txt` is append-only to preserve history
- **No temporary files**: The agent is instructed not to create temporary `progress_*.txt` files

## Files and Templates

- **`ralph_claude`**: Bash script implementing the loop for Claude Code CLI
- **`PROMPT.md`**: Instructions given to the agent on each iteration
- **`PROMPT_TEMPLATES.md`**: Templates for implementing with other AI agents (GPT, Gemini, etc.)
- **`PRD-PROMPT.md`**: Comprehensive guide for creating effective PRDs
- **`plans/example-prd.json`**: Example PRD structure with sample tasks

## PRD Best Practices

- **Be specific**: Not "add auth" but "implement JWT token refresh endpoint"
- **Define steps**: Break each task into 3-5 concrete steps
- **One feature per task**: Keep tasks atomic and deployable
- **Order by priority**: Most important tasks first

## References

- [Original Ralph Wiggum article](https://ghuntley.com/ralph/)
- [Anthropic: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Matt Pocock's YouTube: Ralph Wiggum Technique](https://www.youtube.com/watch?v=_IK18goX4X8)

## License

MIT

---

**Ralph Wiggum**: *"I'm in danger!"* ⚠️
