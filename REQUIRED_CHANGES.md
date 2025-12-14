# Required Changes to paper.md

## Summary of Findings from Repository

### ✅ Verified Information
- **Dataset**: 240 questions confirmed (240 entries in dataset.json)
- **Output Files Generated**:
  1. `results.csv` - Raw model outputs (11,699 rows = 2,160 queries + 1 header)
  2. `scored_results.csv` - Normalized and scored results with additional columns (gold_norm, pred_norm, correct)
  3. `tables/accuracy_by_model_prompt.csv` - Model × prompt type accuracy breakdown
  4. `tables/accuracy_by_model_task.csv` - Model × task accuracy breakdown
  5. `tables/cot_delta_by_model.csv` - CoT vs Direct performance delta
  6. `figures/accuracy_vs_difficulty.png` - Figure 1 showing accuracy across difficulty levels
  7. `figures/accuracy_by_task.png` - Figure 2 showing accuracy across task categories
  8. `figures/cot_failure_examples.csv` - 5,043 cases where direct succeeded but CoT failed

### Answer Extraction Logic Analysis

**Current Implementation (evaluate_results.py, lines 23-37)**:

```python
def normalize(text):
    if pd.isna(text):
        return ""

    text = str(text).lower().strip()

    # yes / no normalization
    if text.startswith("yes"):
        return "yes"
    if text.startswith("no"):
        return "no"

    # numeric extraction (ints / floats)
    numbers = re.findall(r"-?\d+\.?\d*", text)
    if numbers:
        return numbers[0]  # ← RETURNS FIRST NUMBER FOUND

    # remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()
```

**Key Behavior**:
- Extracts **first numeric value found** using regex `-?\d+\.?\d*`
- Does NOT prioritize "Final Answer:", "Therefore:", or explicit markers
- Does NOT look at the end of the response for the final answer
- Example: "Step 1: 6 + 9 = 15" extracts "1" (from "Step 1"), not "15"

**Paper Description Accuracy**:
- Paper (Section 3.4): "Extract numeric values using regex: `-?\d+\.?\d*`" ✅ Correct
- Paper (Section 5.2.1): "extracts the first number it finds" ✅ Correct
- Paper (Section 5.2.2): "extracts "14" (the first number mentioned) instead of "9"" ✅ Correct

---

## Required Changes to paper.md

### CHANGE 1: Standardize Model Names to Shorter Format

**Current**: Mix of full and short names
- Full: `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, `meta-llama/llama-4-maverick-17b-128e-instruct`
- Short: `llama-3.1-8b`, `llama-3.3-70b`, `llama-4-maverick`

**Proposed**: Use short names everywhere

**Locations to Change**:
1. Section 3.3 (Models Evaluated) - Model descriptions
2. Section 4.1 - Table 1 rows
3. Section 4.2 - Table 2 rows
4. Section 4.3 - Table 3 rows
5. Section 4.5 - Summary bullet points
6. Section 7.2 - Related findings
7. Appendix A.1, A.2, A.3 - All tables

**Mapping**:
- `llama-3.1-8b-instant` → `llama-3.1-8b`
- `llama-3.3-70b-versatile` → `llama-3.3-70b`
- `meta-llama/llama-4-maverick-17b-128e-instruct` → `llama-4-maverick`

---

### CHANGE 2: Fix Figure References and Add Titles

**Current** (Section 4.4):
```
Figure 1 illustrates measured accuracy as a function of task difficulty (easy, medium, hard).
```

**Required Changes**:
1. **Section 4.4** - Map to correct file and add title:
   - Figure 1 → `figures/accuracy_vs_difficulty.png`
   - Title: "Measured Accuracy vs Task Difficulty"

2. **After Section 4.4** - Add Figure 2 reference (currently missing):
   - Add new subsection or reference in 4.5
   - Figure 2 → `figures/accuracy_by_task.png`
   - Title: "Measured Accuracy by Task Category"

3. **Appendix C** - Update with titles:
   ```
   - Figure 1 (`figures/accuracy_vs_difficulty.png`): Measured Accuracy vs Task Difficulty
   - Figure 2 (`figures/accuracy_by_task.png`): Measured Accuracy by Task Category
   ```

---

### CHANGE 3: Add Data/Code Availability Statement

**Location**: Add new subsection after Methodology, before Results (after Section 3.5 or as part of it)

**Proposed Text**:
```markdown
### 3.6 Reproducibility and Data Availability

All code, data, and results are available at: https://github.com/Kabir08/cot-hurts-performance

**Generated Output Files**:
- `results.csv`: Raw model outputs for all 2,160 queries (model, prompt_type, question, gold_answer, model_output)
- `scored_results.csv`: Evaluated results with normalized answers and correctness scores
- `tables/accuracy_by_model_prompt.csv`: Aggregated accuracy by model and prompting strategy
- `tables/accuracy_by_model_task.csv`: Aggregated accuracy by model and task category
- `tables/cot_delta_by_model.csv`: Performance delta (CoT − Direct) for each model
- `figures/cot_failure_examples.csv`: 5,043 cases where direct prompting succeeded but CoT failed, with full outputs for analysis
- `figures/accuracy_vs_difficulty.png`: Figure 1 - Accuracy breakdown by task difficulty
- `figures/accuracy_by_task.png`: Figure 2 - Accuracy breakdown by task category

**Reproducibility**: The experimental results can be reproduced by running `run_experiment.py` (requires Groq API access) followed by `evaluate_results.py`.
```

---

### CHANGE 4: Enhance Section 3.5 to Describe Output Files

**Current Section 3.5** (too brief):
```
- Total queries: 2,160 (3 models × 240 questions × 3 prompt types)
- Data collection: Streaming API queries to Groq
- Scoring: Post-hoc normalization and exact-match evaluation
- Visualization: Matplotlib-based figures and CSV tables
```

**Proposed Enhancement**:
```
### 3.5 Experiment Execution

- **Total queries**: 2,160 (3 models × 240 questions × 3 prompt types)
- **Data collection**: Streaming API queries to Groq
- **Scoring**: Post-hoc normalization and exact-match evaluation
- **Output**: Raw results stored in `results.csv` with columns: model, prompt_type, id, task, difficulty, question, gold_answer, model_output
- **Evaluation**: Responses normalized using the pipeline described in Section 3.4, then compared against gold answers
- **Visualization**: Matplotlib-based figures (Figures 1-2) and CSV summary tables saved to `tables/` and `figures/` directories
```

---

### CHANGE 5: Clarify Answer Extraction Logic in Section 3.4

**Current Text** (Section 3.4, Answer Normalization):
```
3. Extract numeric values using regex: `-?\d+\.?\d*`
```

**Proposed Enhancement**:
```
3. Extract numeric values using regex: `-?\d+\.?\d*`, returning the first match found in the text
```

**Add explanatory note after the pipeline**:
```
Note: The normalization pipeline prioritizes extracting the first numeric value encountered in the normalized text. 
This design choice, while effective for direct prompts that produce terse answers, contributes to failures when 
evaluating verbose CoT responses that contain multiple intermediate numeric values before the final answer 
(see Section 5.2 for detailed failure analysis).
```

---

### CHANGE 6: Add Explicit Discussion of Output Files in Section 5.2

**Location**: After Section 5.2.3 (Confusion from Multiple Numbers), before 5.3

**Proposed Addition**:
```markdown
### 5.2.4 Quantification of Failures

To systematically analyze these failure patterns, we extracted all cases where direct prompting succeeded (correct answer) 
but CoT prompting failed (incorrect answer under automated evaluation). This analysis identified 5,043 failure cases across 
all models and tasks. Detailed examples with full model outputs are available in `figures/cot_failure_examples.csv` 
for further analysis and inspection.
```

---

### CHANGE 7: Enhance Section 6.7 Limitations with More Detail

**Current Section 6.7** (too brief):
```
While we identify evaluation mismatch as a primary driver of measured CoT failures, several limitations remain:

Our answer extraction pipeline is intentionally simple and may not reflect best practices.

We do not perform human evaluation to verify correctness of intermediate reasoning.

The study focuses on a limited set of models and tasks.
```

**Proposed Enhancement**:
```
### 6.7 Limitations Revisited

While we identify evaluation mismatch as a primary driver of measured CoT failures, several limitations remain:

**Evaluation methodology**: Our answer extraction pipeline is intentionally simple and may not reflect best practices. 
The first-match numeric extraction heuristic (Section 3.4) was designed for terse direct responses and is known to fail 
on verbose outputs. More sophisticated extraction methods (LLM-based scoring, regex patterns tuned to each task type, 
or explicit answer markers) could substantially improve measured CoT performance.

**Intermediate reasoning verification**: We do not perform human evaluation to verify whether intermediate reasoning 
steps in failed CoT responses are actually correct before extraction failure occurs. Such verification would help 
quantify how much of the degradation stems from reasoning errors vs. extraction artifacts.

**Model and task scope**: The study focuses on three Llama-family models and four task categories with relatively short-form 
answers. Results may not generalize to other architectures (e.g., GPT, Claude, Gemini) or task types with longer, more 
structured answers (e.g., multi-paragraph essays, code generation).

**Hyperparameter sensitivity**: We fix temperature at 0.2 (deterministic decoding). CoT prompts may have different 
sensitivity profiles at higher temperatures or with different max_tokens settings.

**Zero-shot evaluation**: We evaluate only zero-shot prompting without in-context examples. Few-shot CoT, which has shown 
benefits in prior work, may exhibit different patterns.
```

---

### CHANGE 8: Add Explicit Mapping of Failure Examples to Output Files

**Location**: Update Appendix B

**Current**:
```
See `figures/cot_failure_examples.csv` for a complete list of 5,043 cases...
```

**Proposed Enhancement**:
```
## Appendix B: Example Failure Cases

The file `figures/cot_failure_examples.csv` contains 5,043 cases where direct prompting succeeded but CoT failed 
(measured accuracy under automated evaluation). This dataset includes:
- **Columns**: model, prompt_type (direct or cot), id, task, difficulty, question, gold_answer, model_output, 
  gold_norm, pred_norm, correct
- **Filtering**: Rows represent instances where prompt_type ∈ {direct, cot} for cases where direct=1 (correct) 
  and cot=0 (incorrect)

Researchers can use this file to:
1. Understand specific failure patterns
2. Develop improved answer extraction heuristics
3. Analyze reasoning quality even when extraction fails
4. Design task-specific evaluation procedures
```

---

## Summary Table: All Changes

| # | Type | Location | Change | Priority |
|---|------|----------|--------|----------|
| 1 | Content | Sections 3.3, 4.1, 4.2, 4.3, 4.5, 7.2, Appendix | Standardize model names to short format | **HIGH** |
| 2 | Content | Sections 4.4, 4.5, Appendix C | Map figures correctly with titles (Figure 1 & 2) | **HIGH** |
| 3 | Content | After 3.5 or as new 3.6 | Add code/data availability statement | **MEDIUM** |
| 4 | Content | Section 3.5 | Enhance to describe output files | **MEDIUM** |
| 5 | Content | Section 3.4 | Clarify answer extraction order & add note | **MEDIUM** |
| 6 | Content | Section 5.2.4 (new) | Add quantification of failures with CSV reference | **MEDIUM** |
| 7 | Content | Section 6.7 | Expand limitations with detailed analysis | **MEDIUM** |
| 8 | Content | Appendix B | Enhance with CSV column details and use cases | **LOW** |

---

## Questions for Approval

1. **Model naming**: Approve standardizing to `llama-3.1-8b`, `llama-3.3-70b`, `llama-4-maverick`?

2. **Figure placement**: Should Figure 2 reference be added as a new subsection 4.4.5, or incorporated into 4.5?

3. **Data availability**: Should the new section be 3.6 or integrated into existing 3.5?

4. **Limitations section**: Should I expand Section 6.7 as proposed, or keep it more concise?

5. **Failure examples**: Should Appendix B be expanded with column details and use cases?

6. **Output files description**: Approve adding enhanced Section 3.5 describing generated files?

Once you approve these changes, I can implement them all efficiently.
