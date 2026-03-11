# Task 1: Audit

## 1. Token Inventory

The following token counts were calculated using the `gemini/gemini-3.1-pro-preview` model via the `litellm.token_counter` library method. Rendered token counts include mock variables to properly account for typical context lengths.

| Template Name | Tokens (Raw) | Tokens (Rendered) |
| :--- | ---: | ---: |
| `additional_info.j2` | 470 | 8 |
| `in_context_learning_example.j2` | 1554 | 1561 |
| `in_context_learning_example_suffix.j2` | 27 | 34 |
| `microagent_info.j2` | 58 | 7 |
| `security_risk_assessment.j2` | 245 | 139 |
| `system_prompt.j2` | 1827 | 1954 |
| `system_prompt_interactive.j2` | 248 | 2192 |
| `system_prompt_long_horizon.j2` | 675 | 2619 |
| `system_prompt_tech_philosophy.j2` | 1082 | 3026 |
| `user_prompt.j2` | 0 | 7 |

- Note: Templates like additional_info.j2 show a significant drop in rendered tokens because they are conditional. This indicates 'Hidden Dead Weight'—logic that only triggers in specific edge cases, adding complexity to the codebase while remaining inactive for most tasks.
- The Tech Philosophy template is the primary source of context inflation, tripling in size upon rendering. This points to a lack of hierarchy; the model is being fed 'philosophical' overhead that consumes nearly 30% of the total prompt budget.
- The system utilizes multiple high-token system prompt variants. There is a high risk of 'Instruction Dilution' where the core CodeAct instructions are buried under specialized behavior prompts (Interactive vs. Long Horizon)

### Key Inventory Observations:

1. **Instructional Overhead**: The total rendered system context (summing the active templates) exceeds 10,000 tokens in some configurations. This significantly increases latency and cost per turn.

2. **Conditional Fragmentation**: Several templates (e.g., additional_info.j2) contain substantial logic that rarely renders, indicating the prompt suite has become a "catch-all" for edge cases.

3. **The Philosophy Tax**: system_prompt_tech_philosophy.j2 is the single most expensive component when rendered. An audit of this file is required to see if these 3,000 tokens provide a proportional increase in success rate.

## 2. Redundancy Map

| Concept | Found in | Locations | The Conflict/Overlap |
| :--- | :--- | :--- | :--- |
| **File Modification** | `system_prompt.j2` | `<FILE_SYSTEM_GUIDELINES>`, `<PROBLEM_SOLVING_WORKFLOW>` | The instruction to never create files with different suffixes and to modify original files directly is repeated almost verbatim. |
| **Documentation Rules** | `system_prompt.j2` | `<FILE_SYSTEM_GUIDELINES>`, `<DOCUMENTATION>` | The rule prohibiting committing documentation into VC is stated first and then restated later. |
| **External Services** | `system_prompt.j2` | `<SECURITY>`, `<EXTERNAL_SERVICES>` | Both redundantly state to use APIs instead of browser-based interactions for GitHub/external platforms. |
| **Tool Usage (`sed`)** | `system_prompt.j2` | `<EFFICIENCY>`, `<FILE_SYSTEM_GUIDELINES>` | Recommends using `sed`/`grep` to edit files, and overlaps heavily by recommending `sed` again for search-and-replace. |
| **Task Status Updates** | `system_prompt_long_horizon.j2` | `<TASK_MANAGEMENT>` | Demands immediate "done" status updates in the preamble, and then uselessly repeats the exact instruction in workflow step 4. |
| **Backward Compatibility** | `system_prompt_tech_philosophy.j2` | `# My Core Philosophy`, `# Requirement Confirmation Process` | "Never break userspace" is stated as Iron Law #2, and redundantly listed in Layer 4 of the Requirement Confirmation Process. |
| **Ask for Clarification** | `system_prompt.j2`,<br>`system_prompt_interactive.j2` | `<TROUBLESHOOTING>`, `<INTERACTION_RULES>` | One says to confirm the plan if stuck; the other repeats a similar safety net asking the agent to clarify if unsure of intent. |
| **The "Exploration" Rule (3x)** | `system_prompt.j2`,<br>`system_prompt_interactive.j2` | `<CODE_QUALITY>`, `<PROBLEM_SOLVING_WORKFLOW>`, `<INTERACTION_RULES>` | The agent is being told to look before it leaps three separate times across different XML tags. |
| **The Temporary File Rule** | `system_prompt.j2` | `<FILE_SYSTEM_GUIDELINES>`, `<PROBLEM_SOLVING_WORKFLOW>` | "If you need to create a temporary file for testing, delete it once you've confirmed your solution works" is repeated almost word-for-word. |
| **The `{% include %}` Trap** | `system_prompt_interactive.j2`,<br>`system_prompt_long_horizon.j2`,<br>`system_prompt_tech_philosophy.j2` | Template Headers | All variants start by importing `system_prompt.j2`. If OpenHands accidentally loads the base AND a variant simultaneously, the entire base prompt is duplicated. |

## 3. Dead Weight

Prompt templates often accumulate "scar tissue"—instructions added to patch older model failures (like GPT-3.5) that modern models handle natively. Reviewing the templates reveals significant dead weight:

### Over-explanation (Basic Coding Principles)

Modern LLMs inherently understand basic software engineering practices. The instructions below unnecessarily consume context:

- **`system_prompt.j2`** `<CODE_QUALITY>`:
  - *"Write clean, efficient code with minimal comments. Avoid redundancy in comments: Do not repeat information that can be easily inferred from the code itself."*
  - *"Place all imports at the top of the file unless explicitly requested otherwise..."*
  - *"If working in a git repo, before you commit code create a .gitignore file if one doesn't exist."*

- **`system_prompt_tech_philosophy.j2`**:
  - The entire "Linus Torvalds" persona is essentially ~3,000 rendered tokens of over-explanation. Emphasizing basic principles like "functions must be short," "simplest solution," and "backward compatibility" via a complex, multi-layered roleplay wrapper is redundant for top-tier models that already default to standard clean code practices.

### Negative Constraints (The "Don't" Anti-Pattern)

Modern models generally respond better to positive instructions ("Do Z") rather than an excessive list of negative constraints ("Don't do X or Y"). The prompts contain a vast number of harsh negative limitations:

- **`system_prompt.j2`**:
  - `<FILE_SYSTEM_GUIDELINES>`: *"do NOT assume it's relative..."*, *"NEVER create multiple versions..."*, *"Do NOT include documentation files..."*
  - `<VERSION_CONTROL>`: *"Do NOT make potentially dangerous changes..."*, *"Do NOT commit files that typically shouldn't go into version... (e.g., node_modules/, .env files...)"*
  - `<PULL_REQUESTS>`: *"**Important**: Do not push to the remote branch... create only ONE per session..."*
  - `<PROCESS_MANAGEMENT>`: *"Do NOT use general keywords with commands like `pkill -f server`..."*

### Format Hand-holding

- **`in_context_learning_example_suffix.j2`**:
  - *"PLEASE follow the format strictly! PLEASE EMIT ONE AND ONLY ONE FUNCTION CALL PER MESSAGE."*
  - Begging older models with all-caps "PLEASE" to follow a rigid JSON/function call format is classic scar tissue. Modern capability models follow structured output schemas natively without needing emotional pleas.

## 4. Structural Critique

When reading the assembled prompt context as a single LLM input, several structural anti-patterns emerge that degrade instruction coherence:

### The "Changelog" Smell

The prompt feels significantly fragmented, resembling a list of rules appended over time rather than a cohesive strategy document.
- **Role Identity Crisis:** `system_prompt.j2` starts by establishing the agent as a "helpful AI assistant." However, if `system_prompt_tech_philosophy.j2` is injected, the agent is suddenly commanded to adopt the rigid persona of Linus Torvalds. This creates a massive clash in tone and behavioral expectations.
- **Scattered Guidelines:** Information about the same topics is dispersed across multiple tags. For example, rules about git and version control are split between `<VERSION_CONTROL>` and `<FILE_SYSTEM_GUIDELINES>`. File modification rules are spread between `<FILE_SYSTEM_GUIDELINES>` and `<PROBLEM_SOLVING_WORKFLOW>`.

### Sub-optimal Information Density

- **Primacy/Recency Dilution:** Best practices dictate that the most critical instructions (the absolute goal and format) should be at the very beginning (primacy) or the very end (recency) of the prompt.
- **Buried Core Directives:** The actual core directives for solving a task (found in `<PROBLEM_SOLVING_WORKFLOW>`) are buried in the middle of `system_prompt.j2`, surrounded by edge-case negative constraints (`<SECURITY>`, `<PROCESS_MANAGEMENT>`, `<DOCUMENTATION>`). The LLM is forced to process dozens of "Don'ts" before/after it gets to the actual "How To Do The Task."

### Tone Inconsistency

- **Helpful vs. Hostile/Pleading:** `system_prompt.j2` maintains a somewhat standard, neutral, "helpful assistant" tone. Conversely, `system_prompt_tech_philosophy.j2` aggressively shifts to a highly opinionated, sharp, and commanding tone ("I'm a damn pragmatist," "you're screwed"). Meanwhile, `in_context_learning_example_suffix.j2` uses desperate all-caps pleading ("PLEASE follow the format strictly!"). The model is pulled in three incredibly different emotional directions within the same context window.
