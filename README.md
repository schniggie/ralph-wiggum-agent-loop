# Ralph Wiggum Agent Loop

A universal, framework-agnostic implementation of the **Ralph Wiggum pattern** - a simple loop-based approach for autonomous coding agents. Works with **any LLM** or coding agent (Claude, GPT, Llama, Gemini, etc.).

Based on Matt Pocock's [Ralph Wiggum technique](https://ghuntley.com/ralph/).

## What is Ralph Wiggum?

Ralph Wiggum is a minimalist approach to autonomous software development that uses:

- **A simple for loop** instead of complex orchestration systems
- **A prioritized task list (PRD)** defining work to be done
- **Git-based progress tracking** using commit messages instead of separate progress files
- **Iterative execution** where each loop:
  1. Reviews git history to understand previous work
  2. Selects the highest-priority incomplete task
  3. Completes the task
  4. Commits work with detailed progress information
  5. Repeats until complete

The pattern mimics how real engineers work: pick a task → complete it → commit it → repeat.

## Key Principles

- **Simplicity**: A basic loop is all you need
- **Feedback Loops**: Tests, type checking, and CI ensure code quality
- **Single Focus**: Only work on one task per iteration
- **Git-Based Progress**: Commit messages serve as progress documentation
- **Atomic Commits**: Each completed task gets its own descriptive commit with implementation details

## Project Structure

```
.
├── README.md              # This file
├── PROMPT.md              # Agent instructions
├── PRD-PROMPT.md          # Detailed PRD creation guide
├── PROMPT_TEMPLATES.md    # Prompt templates for other agents
├── ralph_claude           # Claude Code CLI implementation script
├── ralph_kiro             # Kiro CLI implementation script
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

### 2. Run the Loop

#### Using Claude Code CLI:

```bash
./ralph_claude 50  # Run 50 iterations
```

#### Using Kiro CLI:

```bash
./ralph_kiro 50  # Run 50 iterations
```

Both scripts will:
- Read your PRD via the PRD service API
- Review git commit history for context
- Select the highest-priority task
- Implement it completely
- Run tests and type checks
- Commit the changes with detailed progress information
- Repeat

For other AI agents (GPT, Gemini, etc.), see `PROMPT_TEMPLATES.md` for implementation guidance.

## How It Works

1. **Backup**: Before each iteration, `prd.json` is backed up to `../.backup/` with iteration counter in filename
2. **Loop starts**: Agent reads PRD via service API and reviews git commit history
3. **Task selection**: Agent picks highest-priority incomplete task
4. **Implementation**: Agent completes the task, runs tests, makes commit with detailed message
5. **Progress update**: Agent updates PRD via service API (marks task as passed) and commits with structured message
6. **Repeat**: Loop continues until all tasks complete or max iterations reached

### Safety Features

- **Automatic backups**: `prd.json` is backed up before each iteration to `../.backup/prd_iteration_N.json`
- **PRD Service API**: All PRD modifications go through the service, preventing file corruption
- **Git-based history**: Progress is tracked in commit messages, which are immutable and always append-only
- **Structured commits**: Agents use a standardized commit message format for consistency

## Implementation Scripts

This repository includes two ready-to-use implementation scripts:

### `ralph_claude`
Bash script implementing the Ralph Wiggum loop for **Claude Code CLI**:
- Uses `claude` command with `--permission-mode acceptEdits`
- Passes PROMPT.md to Claude on each iteration
- Agent reads git history for progress context
- Includes automatic PRD backups and completion detection

### `ralph_kiro`
Bash script implementing the Ralph Wiggum loop for **Kiro CLI**:
- Uses `kiro-cli chat` with `--no-interactive --trust-all-tools`
- Passes PROMPT.md content to Kiro on each iteration
- Agent reads git history for progress context
- Includes automatic PRD backups and completion detection

Both scripts support:
- Configurable iteration limits
- Automatic PRD backups (git provides commit history backup)
- Completion detection via `<promise>COMPLETE</promise>` marker
- Validation that all tasks pass before exit

## Files and Templates

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
