# 📚 LLM Story Generator — Operator Guide

You collaborate with an AI agent to build a story in clear stages  
(Character Bible → Premise → Beat Sheet → Scenes → Revision).

Use with Claude Code, OpenAI Codex, etc. Make sure the agent reads and follows the instructions in `AGENTS.md`.

**No command-line steps are required from you.**

---

## Workflow

1. **Agent greets you**  
   It identifies the current stage and summarizes the latest accepted story state.

2. **Answer refinement questions**  
   The agent asks 5-10 targeted questions (what to keep, what to vary).

3. **Review three synopses**  
   The agent shows A/B/C bullet pitches plus a brief self-critique.

4. **Pick a favourite**  
   Say something like “Let’s go with Pitch B”.

5. **Confirm canon**  
   The agent will ask:  
   `Ready to make Pitch B canon?`  
   – Reply **yes** (or ask for further tweaks).

6. **Agent updates the repo**  
   It archives unused files, validates structure, patches the modular XML,  
   and moves to the next stage—all automatically.
