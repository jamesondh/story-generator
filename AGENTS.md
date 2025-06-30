# AGENTS.md – LLM‑Driven Story Repo Orchestration Guide

> **Purpose**: This file tells **whichever LLM is currently responding how to create and modify files inside this Git repository during the goal‑driven story‑generation process steered by an operator.** All rules are provider‑agnostic; the only provider‑specific detail required is a short signature so operators can see which LLM generated which artefact.

---

## 1 Repository top‑level map

```text
repo/
├── prompts/                    # static templates & generation knobs
│   ├── templates/
│   │   └── StoryPrompt_v0.4.xml
│   └── config/
│       └── llm_config.xml      # temperature, penalties, etc.
├── story/
│   ├── current/                # **only** canonical, modular XML
│   │   ├── themes.xml
│   │   ├── world.xml
│   │   ├── characters.xml
│   │   ├── plot.xml
│   │   ├── mechanics.xml
│   │   └── story_nav.xml       # small index that XIncludes the above
│   ├── character-bible/        # stage‑specific variation dumps
│   ├── premise/
│   ├── beat-sheet/
│   ├── scenes/
│   └── archive/                # auto‑moved discarded variations
├── scripts/
│   ├── generate_variations.py  # CLI wrapper → calls LLM step‑by‑step
│   ├── validate_output.py      # schema & naming compliance checker
│   └── archive_old_files.py    # housekeeping after acceptance
├── tests/                      # unchanged – add schemas as needed
├── AGENTS.md                   # (this guide)
└── README.md                   # operator guide
```

### 1.1 Why two “character” places?

- **`story/current/characters.xml`**  
  Canonical facts for every accepted character.  
  _Always_ load this file when you need ground-truth about the cast.

- **`story/character-bible/` (stage workspace)**  
  Temporary variations and critiques produced **only** during the
  **CHARACTER_BIBLE** stage.  
  These files are _drafts_ — they disappear into `story/archive/`
  once a final version is accepted.

The same pattern holds for every stage:

| Canonical source               | Draft workspace     |
| ------------------------------ | ------------------- |
| `story/current/themes.xml`     | `story/premise/`    |
| `story/current/plot.xml`       | `story/beat-sheet/` |
| `story/current/*.xml` (scenes) | `story/scenes/`     |

**Rule of thumb**

> _“Read from `story/current/` when you need facts; read from the stage
> workspace when you need OPTIONS.”_

This lets the LLM load **just enough context**:

- When tweaking a single character detail, open:

  1. `story/current/characters.xml` to ensure consistency.
  2. The specific draft variation file you are patching.
     You **do not** need to parse every scene or the entire plot file.

- When generating a new scene, load:
  1. `story/current/plot.xml` (beats).
  2. `story/current/characters.xml` (quick cast lookup).
  3. `story/current/world.xml` (setting touch-points).

By default, helper scripts hand the LLM exactly those paths, so it
doesn’t waste context window on irrelevant minutiae.

> **Tip for implementers**: internal helper modules expose  
> `load_canon(*paths)` and `load_workspace(stage)` utilities to keep this
> disciplined.

---

## 2 LLM identity & signatures

To keep provenance clear:

- Use timestamp‑based naming for EVERY new file (except current.xml):\
  Format: `{STAGE}_{label}_{YYYYMMDD}_{HHMM}_{llm}.xml|md`\
  Example: `PREMISE_Pitch_A_20250630_1832_gpt‑4o.xml`
- NEVER overwrite existing files. Each generation gets a new timestamp.

---

## 3 Four‑step pipeline (per IterationStage)

| Step         | Agent must…                                                                                                                                                                          | Output files                        |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| **REFINE**   | Ask 5‑10 targeted questions → build `<RefinementMatrix>` in memory (don’t save yet).                                                                                                 | none                                |
| **GENERATE** | Produce **3** labelled variations adhering to the matrix.                                                                                                                            | `story/<Stage>/…Pitch_A…C.xml`      |
| **CRITIQUE** | Evaluate each variation (Novelty, Coherence, ThemeFit, GoalAdherence). Propose prompt tweaks (theme weights, penalties, etc.).                                                       | `{STAGE}_critique_{timestamp}.md`   |
| **APPLY**    | After operator picks a variation: <br>• copy chosen file’s delta into relevant `story/current/*.xml` <br>• run `scripts/archive_old_files.py` <br>• run `scripts/validate_output.py` | updated canonical XML; no new files |

---

## 4 Helper commands

The **host script** orchestrates calls to the LLM so it never skips a step.

```bash
# generate 3 premise variations, critique, wait for operator:
python scripts/generate_variations.py PREMISE

# once operator selects 'B', apply & clean:
python scripts/archive_old_files.py PREMISE Pitch_B_20250630_1832_gpt-4o.xml
python scripts/validate_output.py
```

---

## 5 Forbidden Actions

- Overwriting any file in `story/current/` without explicit operator “canon‑confirm”.
- Writing outside the allowed directories.
- Skipping the CRITIQUE or APPLY phases.

---

## 6 Operator override signals

Operators may place comments in any XML or Markdown file:

```xml
<!--LLM‑DIRECTIVE: SKIP_NEXT_VARIATION-->
```

The LLM must obey these directives.

---

## 7 Quick start for the LLM (cheat‑sheet)

The steps below are for **the agent itself**.  
The human operator never calls repository scripts directly.

1. **Read** `story/current/story_nav.xml` (index of themes.xml, world.xml, etc.) and this file.  
   The `<ProjectState iteration_stage="…"/>` attribute indicates the active stage.
2. **Identify** the current `iteration_stage`.
3. **REFINE → GENERATE → CRITIQUE**  
   Call the helper modules (or subprocess scripts) in this order:
   - `generate_variations.py --stage <STAGE>`
   - `validate_output.py` (post-generation sanity)  
     – All of this happens silently from the operator’s perspective.
4. **Present** the three labelled synopses plus a concise critique summary to the operator.
5. **Await** operator selection (e.g. “I like Pitch B”).
6. **APPLY**  
   On confirmation, internally invoke:
   - `archive_old_files.py <STAGE> <ACCEPTED_FILENAME>`
   - `validate_output.py` (again, after patching)
   - Update the relevant XML in `story/current/`.  
     Confirm completion to the operator (“Pitch B is now canon. Stage advanced.”).
7. **Exit** or proceed to the next stage, as directed by the operator.

> **Note:** If running inside a sandbox that can’t spawn Python, port these scripts to inline functions.  
> Contract: all validation/archiving must succeed before the agent signals “Done”.

---

## 8 Conversational Interface Rules (provider-agnostic)

**Goal:** keep XML / schema noise invisible; speak plain English with the operator.

### 8.1 Startup handshake

When the agent wakes up **inside an interactive chat** (not via script):

1. Load `story/current/story_nav.xml` and determine `iteration_stage`.
2. Greet the operator with:
   - **One-sentence** summary of the current stage (e.g. “We’re at the Premise stage.”).
   - **One-paragraph** recap of the last accepted artefact (pull from the relevant modular XML).
   - **Numbered list** of valid next actions, e.g.
     1. Generate new variations
     2. Review last critique
     3. Advance to next stage

### 8.2 Asking & confirming

- Ask questions in plain English.
- Echo the interpreted answer for confirmation, e.g.:  
  `**So we will keep all characters unchanged and only vary the central conflict, correct?**`  
  Proceed **only after** operator affirmation.

### 8.3 Pre-variation refinement questionnaire

Follow the four-step pipeline (REFINE->GENERATE->CRITIQUE->APPLY).  
During **REFINE**:

1. Ask **5-10** targeted questions to build the `<RefinementMatrix>`:
   - “Should we lean more toward cosmic horror or moral agency?”
   - “Keep The Nine exactly as they are?”
   - “Focus on an action climax or a philosophical resolution?”  
     _(etc.)_
2. Present questions in batches of **1–3** at a time.
3. Summarize:  
   `**Based on your answers I'll vary [X], keep [Y], maintain [Z]. Proceed?**`
4. Only after _yes_, continue to GENERATE.

### 8.4 Generation & presentation

- Produce exactly the mandated **3 labelled variations** (`Pitch_A`, `Pitch_B`, `Pitch_C`).
- Show the operator **bullet synopses**; hide raw XML.
- Ensure each variation respects the `<Lock>` vs `<Vary>` directives from the `RefinementMatrix`.

### 8.5 Canon confirmation

- Ask:  
  `**Ready to make Pitch B canon? This will update the modular XML and advance the story stage.**`
- On **yes**, run the APPLY sequence (archive → validate → patch XML) **internally**.
- If the operator says **no**, loop back to REFINE or GENERATE as requested.

---

> **Remember:** your outputs become part of the codebase. Treat each run like a deterministic build step—**idempotent, diff‑friendly, and fully traceable.**

_(end of AGENTS.md)_
