# Prompt Optimization Changelog

This document tracks the changes made to the system prompts to optimize token usage and improve model instruction adherence by shifting from a "philosophical/hostile" tone to a neutral, instruction-heavy format.

| Change | Action | Reasoning |
| :--- | :--- | :--- |
| **Removed `system_prompt_tech_philosophy.j2`** | Deleted the entire file. | This template contained excessive philosophical "fluff" and adopted a "hostile/pleading" tone referencing Linus Torvalds. Large language models perform better with direct, neutral, and actionable instructions. The philosophical preamble consumed prompt budget without adding concrete constraints, leading to severe contextual inflation (tripling its token footprint). |
| **Consolidated Technical Philosophy** | Extracted core pragmatic directives into a new `<TECHNICAL_PHILOSOPHY>` section in `system_prompt.j2`. | Instead of injecting a separate template with verbose guidelines, the actionable software engineering rules (e.g., short functions, no edge cases, backward compatibility) were distilled into a single, concise bulleted list. This maintains strict coding standards in a dense, token-efficient format without persona roleplay. |
| **Merged Global Constraints** | Combined `<FILE_SYSTEM_GUIDELINES>`, `<VERSION_CONTROL>`, and `<PROBLEM_SOLVING_WORKFLOW>` into `<OPERATIONAL_GUIDELINES>` in `system_prompt.j2` | The instructions from three separate tags were grouped under a single tag with logical headers. Overlapping instructions about temporary files, suffixes, and documentation were deduplicated. This reduces token overhead from repeated XML block tags/introductory phrases, increasing information density. |
| **Trimmed In-Context Examples** | Trimmed code blocks in `in_context_learning_example.j2`. | The file was an extensive 1,561 tokens showing a full implementation of a Flask app. Showing the full implementation of a complex task is unnecessary "dead weight". Presenting a condensed, generic interaction (creating a script) illustrates the pattern of the thought process and tool usage format while saving massive token overhead. |
| **Left Core Guidelines Untouched** | Kept the remaining sections of `system_prompt.j2` (e.g., `<ROLE>`, `<EFFICIENCY>`, `<CODE_QUALITY>`, etc.) as they were. | These sections were already formatted as clear, neutral instructions without substantial overlap in the merged subset. Modifying these might break core agent behaviors, as they correctly prioritize direct actions over abstract reasoning. |
| **Removed Unused Variant Prompts** | Deleted `system_prompt_interactive.j2`, `system_prompt_long_horizon.j2`, and `in_context_learning_example_suffix.j2`, and cleaned up reference logic in `agent_config.py`. | These variants either redundantly repeated the core CodeAct instructions or contained legacy formatting pleas (like begging the model in all-caps), adding excessive token bloat and causing "Instruction Dilution" per the audit. They are no longer necessary with a strong, centralized `system_prompt.j2`. |

## Updated Token Inventory

| Template Name | Tokens (Raw) | Tokens (Rendered) |
| :--- | ---: | ---: |
| `additional_info.j2` | 470 | 8 |
| `in_context_learning_example.j2` | 258 | 265 |
| `microagent_info.j2` | 58 | 7 |
| `security_risk_assessment.j2` | 245 | 139 |
| `system_prompt.j2` | 1833 | 1960 |
| `user_prompt.j2` | 0 | 7 |

- Total Raw Tokens - 2864
- Total Rendered Tokens - 2386
