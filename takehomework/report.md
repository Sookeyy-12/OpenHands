# OpenHands Prompt Optimization & Evaluation Report

## 1. Cut and Re-evaluate

**Goal**: Reduce token count meaningfully (target >20% reduction) without degrading task performance on SWE-bench.

### Results Table

| Prompt Variant | Token Count (Rendered) | SWE-bench Score | Notes |
| :--- | :--- | :--- | :--- |
| **Original** | ~11,547 | [Enter Score Here] | Baseline performance with all legacy constraints, philosophical preambles, and extended in-context examples. |
| **Revised**  |  ~2,386 | [Enter Score Here] | >75% reduction in token count. Extracted core instructions cleanly and removed persona roleplay. |

*(Note: Add the SWE-bench evaluation results to the table above once the evaluation suite run is complete.)*

### Explanation of Performance Impact
*(If performance degrades, detail here what was cut and why it mattered. If performance improves or remains stable, detail how the increased information density helped.)*
[Add your analysis of the SWE-bench results here]

## 2. Change Log

The detailed documentation of every change made to the prompt, including what was removed, what was consolidated, and the explicit reasoning for each action, is maintained in the dedicated `changelog.md` file in this directory.

Please refer to [`changelog.md`](changelog.md) for the complete breakdown.
