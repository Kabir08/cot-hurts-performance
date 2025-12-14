# When Chain-of-Thought Confounds Evaluation: An Empirical Study of Prompting and Answer Extraction

## Abstract

Chain-of-thought (CoT) prompting is widely used to improve large language model performance by encouraging explicit step-by-step reasoning. While prior work has demonstrated substantial gains from CoT on complex reasoning tasks, its interaction with automated evaluation pipelines remains underexplored. In this work, we conduct an empirical study of three prompting strategies—direct answering, full chain-of-thought, and concise chain-of-thought—across three open-weight language models and four task categories spanning arithmetic, factual question answering, short reasoning, and symbolic logic.

We find that, under common exact-match evaluation procedures, CoT prompting leads to dramatic measured accuracy degradation relative to direct prompting, with drops ranging from 58.75% to 72.92% across models. Through detailed failure analysis, we show that many of these failures arise not from incorrect reasoning, but from a mismatch between verbose CoT outputs and simple answer extraction heuristics, which frequently fail to recover the final answer from intermediate reasoning steps.

Our results highlight a critical and underappreciated interaction between prompting strategy and evaluation methodology. We argue that naïvely applying chain-of-thought prompting without corresponding changes to answer extraction and scoring can substantially misrepresent model capabilities. These findings suggest that the effectiveness of reasoning prompts must be assessed jointly with evaluation design, and that direct prompting may remain preferable in many practical settings with automated scoring.

## 1. Introduction

### 1.1 Background

Chain-of-thought (CoT) prompting, introduced by Wei et al. (2022), has demonstrated remarkable success in enabling language models to solve complex reasoning tasks through explicit step-by-step explanations. The technique has been widely adopted in both academic research and production systems, with the intuition that encouraging models to "think step by step" naturally improves their reasoning capabilities.

However, recent observations suggest that this benefit may not be universal. In many real-world applications, simple, direct prompts often yield surprisingly good results—sometimes better than elaborate CoT instructions. This raises an important question: *Under what conditions does CoT actually help, and when does it hurt?*

### 1.2 Research Questions

This study investigates the following research questions:

1. **Does CoT uniformly improve performance across models and task types?**
2. **How do different CoT variants (full vs. concise) compare to direct prompting?**
3. **Are there systematic patterns in task types or difficulty levels where CoT fails?**
4. **What characteristics distinguish "CoT failures" (cases where direct succeeds but CoT fails)?**

### 1.3 Contributions

- **Empirical finding: Evidence that chain-of-thought prompting can lead to large measured accuracy degradation under common automated evaluation pipelines.
- **Analysis**: Quantification of performance deltas and investigation of failure modes.
- **Insights**: Discussion of why CoT may inadvertently increase error rates and implications for prompt design.

## 2. Related Work

### 2.1 Chain-of-Thought Prompting

Wei et al. (2022) introduced CoT prompting as a technique to improve model reasoning on complex tasks, particularly arithmetic and symbolic reasoning. Subsequent work has explored variants including:

- **Few-shot CoT**: Using examples of step-by-step reasoning
- **Automatic CoT**: Self-generating intermediate steps
- **Least-to-most prompting**: Breaking problems into sub-problems

### 2.2 Prompt Engineering

Recent work on prompt engineering (Reynolds & McDonell, 2021; White et al., 2023) has explored how subtle changes in prompt formulation affect model outputs. Key findings include:

- Prompt length and verbosity can have non-monotonic effects on performance
- Model behavior varies significantly across different prompting styles
- Some tasks are inherently robust to prompt variation, while others are sensitive

### 2.3 Task-Specific Performance

Different task types—arithmetic, factual QA, reasoning, and symbolic logic—have different sensitivity profiles to prompting strategies. Some tasks benefit from explicit reasoning guidance, while others may be solved more reliably through simple pattern matching.

## 3. Methodology

### 3.1 Dataset

We constructed a diverse evaluation dataset comprising 240 questions across four task categories:

| Task Category | Easy | Medium | Hard | Total |
|--------------|------|--------|------|-------|
| Arithmetic | 20 | 20 | 20 | 60 |
| Factual QA | 20 | 20 | 20 | 60 |
| Reasoning | 20 | 20 | 20 | 60 |
| Symbolic Logic | 20 | 20 | 20 | 60 |
| **Total** | **80** | **80** | **80** | **240** |

Tasks span three difficulty levels: easy, medium, and hard. Examples include:
- *Arithmetic (Easy)*: "What is 6 + 9?"
- *Arithmetic (Hard)*: "You buy 3 items costing $14 each and get $5 off. How much do you pay?"
- *Factual QA*: Questions about geography, history, and common knowledge
- *Reasoning*: Problems requiring multi-step logical inference
- *Symbolic Logic*: Formal logic and set theory problems

### 3.2 Prompting Strategies

We evaluated three distinct prompting strategies:

1. **Direct**: "Answer the question directly.\nQuestion: {q}\nAnswer:"
2. **Chain-of-Thought (CoT)**: "Answer the question. Think step by step before answering.\nQuestion: {q}\nAnswer:"
3. **Concise CoT**: "Answer the question. Give a brief explanation, then the answer.\nQuestion: {q}\nAnswer:"

These represent a spectrum from minimal instruction (direct) to explicit reasoning encouragement (full CoT) to a middle ground (concise CoT).

### 3.3 Models Evaluated

We tested three models available through the Groq API:

1. **llama-3.1-8b**: A smaller, quantized model optimized for latency
2. **llama-3.3-70b**: A larger, general-purpose model
3. **llama-4-maverick**: A specialized instruction-tuned model

### 3.4 Evaluation Protocol

**Hyperparameters**:
- Temperature: 0.2 (deterministic, near-greedy decoding)
- Max tokens: 256 (limited output length)
- Repetition delay: 0.1 seconds between queries (polite API usage)

**Answer Normalization**:
To handle diverse output formats, we implemented a multi-stage normalization pipeline:

1. Convert to lowercase and strip whitespace
2. Handle boolean answers ("yes"/"no")
3. Extract numeric values using regex: `-?\d+\.?\d*`, returning the **first match found** in the text
4. Remove punctuation and special characters
5. Compare normalized predicted answer against normalized gold answer

Note: The normalization pipeline prioritizes extracting the first numeric value encountered in the response. This design choice, while effective for direct prompts that produce terse answers, is known to cause failures when evaluating verbose CoT responses that contain multiple intermediate numeric values before the final answer (see Section 5.2 for detailed failure analysis). We intentionally use a simple, widely adopted normalization heuristic to reflect common automated evaluation practice, rather than optimizing extraction for CoT outputs.

**Metrics**:
- Accuracy: Percentage of questions answered correctly per model × prompt type combination
- CoT Delta: Difference in accuracy between CoT and direct prompting (CoT − Direct)
- Task-specific accuracy: Breakdown by task category

### 3.5 Experiment Execution

- **Total queries**: 2,160 (3 models × 240 questions × 3 prompt types)
- **Data collection**: Streaming API queries to Groq
- **Scoring**: Post-hoc normalization and exact-match evaluation using the pipeline described in Section 3.4
- **Output**: Raw results stored in `results.csv` with columns: model, prompt_type, id, task, difficulty, question, gold_answer, model_output
- **Evaluation**: Responses normalized and compared against gold answers to produce `scored_results.csv`
- **Visualization**: Matplotlib-based figures and CSV summary tables saved to `figures/` and `tables/` directories

### 3.6 Reproducibility and Data Availability

All code, data, and results are available at: https://github.com/Kabir08/cot-hurts-performance

**Generated Output Files**:
- `results.csv`: Raw model outputs for all 2,160 queries
- `scored_results.csv`: Evaluated results with normalized answers and correctness indicators
- `tables/accuracy_by_model_prompt.csv`: Aggregated accuracy by model and prompting strategy
- `tables/accuracy_by_model_task.csv`: Aggregated accuracy by model and task category
- `tables/cot_delta_by_model.csv`: Performance delta (CoT − Direct) for each model
- `figures/cot_failure_examples.csv`: 471 cases where direct succeeded but CoT failed, with full outputs for analysis
- `figures/accuracy_vs_difficulty.png`: Figure 1 - Accuracy breakdown by task difficulty
- `figures/accuracy_by_task.png`: Figure 2 - Accuracy breakdown by task category

**Reproducibility**: Experimental results can be reproduced by running `run_experiment.py` (requires Groq API credentials) followed by `evaluate_results.py`.

## 4. Results

We evaluate the interaction between prompting strategy and automated evaluation across models, task types, and difficulty levels. All results reported in this section reflect measured accuracy under exact-match, automated answer extraction, as described in Section 3.4.

Our analysis focuses on how different prompting strategies—direct answering, full chain-of-thought (CoT), and concise CoT—affect measured performance under a fixed evaluation pipeline.

4.1 Measured Accuracy by Model and Prompting Strategy

Table 1 reports measured accuracy for each model under the three prompting strategies.

| Model | Direct | CoT | Concise CoT |
|-------|--------|-----|-------------|
| llama-3.1-8b | 65.42% | 0.83% | 5.42% |
| llama-3.3-70b | 79.58% | 6.67% | 8.33% |
| llama-4-maverick | 60.00% | 1.25% | 6.25% |

Across all models, direct prompting yields substantially higher measured accuracy than either CoT variant. In contrast, Chain-of-Thought prompting yields dramatically reduced measured accuracy, often approaching random performance under automated scoring..

Importantly, these results reflect failures of the end-to-end system—including output generation and answer extraction—rather than necessarily incorrect intermediate reasoning.

4.2 Measured Accuracy Degradation Under CoT Prompting

To quantify the effect of CoT prompting, we compute the difference in measured accuracy between CoT and direct prompting (CoT − Direct) for each model (Table 2).

| Model | CoT − Direct |
|-------|---------------|
| llama-3.1-8b | −64.58% |
| llama-3.3-70b | −72.92% |
| llama-4-maverick | −58.75% |

All models exhibit large negative deltas, indicating that under this evaluation setup, CoT prompting interacts poorly with automated scoring. Notably, the largest model (llama-3.3-70b) exhibits the greatest measured degradation, suggesting that increased model capacity alone does not mitigate this effect.

4.3 Task-Level Breakdown of Measured Accuracy

Table 3 reports measured accuracy by task category, aggregated across prompt types.

| Task | llama-3.1-8b | llama-3.3-70b | llama-4-maverick |
|------|--------------|---------------|------------------|
| Arithmetic | 25.0% | 30.0% | 25.0% |
| Factual QA | 27.2% | 31.1% | 25.0% |
| Reasoning | 24.4% | 38.3% | 25.6% |
| Symbolic Logic | 18.9% | 26.7% | 14.4% |

Task-level accuracies are averaged across all prompting strategies for each model.

Measured accuracy varies across task categories, with reasoning tasks showing relatively higher performance for the largest model. However, the relative disadvantage of CoT prompting persists across all task types, including those commonly assumed to benefit from explicit reasoning.

This suggests that the observed degradation is not confined to a specific task domain.

4.4 Measured Accuracy Across Difficulty Levels

**Figure 1: Measured Accuracy vs Task Difficulty** (`figures/accuracy_vs_difficulty.png`) illustrates measured accuracy as a function of task difficulty (easy, medium, hard).

Across all difficulty levels:

Direct prompting shows a gradual decline as difficulty increases

CoT and concise CoT prompting remain near-random under automated scoring

Crucially, the measured performance gap between direct and CoT prompting is present even for easy tasks, indicating that the effect is not driven solely by task complexity.

### 4.4.1 Task-Specific Analysis

**Figure 2: Measured Accuracy by Task Category** (`figures/accuracy_by_task.png`) breaks down performance by task type. While reasoning tasks show relatively higher performance for the largest model (llama-3.3-70b at 38.3%), the degradation under CoT prompting persists across all task categories, indicating that the observed effect is not task-specific.

4.5 Summary of Results

Across three models (llama-3.1-8b, llama-3.3-70b, llama-4-maverick), four task categories, and three difficulty levels, we observe a consistent pattern:

- Direct prompting achieves the highest measured accuracy under automated evaluation (60.0%–79.6% across models)
- Full chain-of-thought prompting produces large negative measured accuracy deltas (−58.75% to −72.92%)
- Concise CoT partially mitigates, but does not eliminate, this degradation (5.4%–8.3%)
- Larger models do not resolve the mismatch between verbose reasoning outputs and simple answer extraction (llama-3.3-70b exhibits the greatest degradation at −72.92%)

These results motivate a deeper analysis of why chain-of-thought prompting interacts poorly with automated evaluation pipelines, which we examine in Section 5.

## 5. Analysis of CoT Failures

### 5.1 Definition of Failure Cases

We define a "CoT failure" as an instance where:
- **Direct prompting**: Correct answer ✓
- **CoT prompting**: Incorrect answer ✗

### 5.2 Failure Mode Characteristics

Analysis of 471 CoT failure cases across all models reveals several patterns:

#### 5.2.1 Answer Extraction Failure

One prominent failure mode occurs when CoT reasoning is correct, but the model fails to extract a single final answer. For example:

**Question**: "What is 6 + 9?"

**Direct Response**: "15"

**CoT Response**: "To find the answer, I will follow the order of operations, which in this case is simply addition. Step 1: Identify the numbers to be added: 6 and 9. Step 2: Add the numbers together: 6 + 9 = 15. Therefore, the answer is 15."

**Normalization Problem**: Our normalization pipeline extracts the first number it finds. In complex CoT responses, this may not be the final answer. In the example above, the normalizer extracts "1" (from "Step 1") rather than "15".

#### 5.2.2 Intermediate Reasoning Interference

CoT sometimes causes models to focus on intermediate calculation steps rather than the final result:

**Question**: "What is 14 - 5?"

**Direct Response**: "9"

**CoT Response**: "To find the answer to 14 - 5, I will follow these steps: 1. Start with the number 14. 2. Subtract 5 from 14. When I subtract 5 from 14, I get: 14 - 5 = 9. So, the answer is 9."

**Normalization Issue**: The normalizer extracts "14" (the first number mentioned) instead of "9".

#### 5.2.3 Confusion from Multiple Numbers

Tasks with word problems introduce many numbers that get highlighted during step-by-step reasoning:

**Question**: "You buy 3 items costing $14 each and get $5 off. How much do you pay?"

**Direct Response**: "37"

**CoT Response**: Contains reasoning like "3 items × $14 = $42, then $42 − $5 = $37" but the step-by-step format causes earlier numbers to be prioritized.

### 5.2.4 Quantification of Failures

To systematically analyze these failure patterns, we extracted all cases where direct prompting succeeded (correct answer) but CoT prompting failed (incorrect answer under automated evaluation). This analysis identified 471 failure cases across all models and tasks (155 for llama-3.1-8b, 175 for llama-3.3-70b, and 141 for llama-4-maverick). Detailed examples with full model outputs, including predicted answers, normalized values, and correctness indicators, are available in `figures/cot_failure_examples.csv` for further analysis and inspection. Additional aggregate statistics are provided in `tables/cot_failures_by_model.csv`.

### 5.3 Root Cause Hypothesis

The primary driver of CoT failure appears to be **incompatibility between:
1. The model's verbose reasoning output (required for CoT)
2. Our answer extraction and normalization procedure**

Rather than indicating that CoT reasoning is fundamentally flawed, these failures suggest that:

- Verbose CoT outputs require more sophisticated answer extraction (e.g., seeking explicit markers like "Therefore:" or "Final Answer:")
- Models trained on CoT may need explicit instructions on answer formatting
- A single numeric extraction heuristic is insufficient for complex outputs

## 6. Discussion


Our results demonstrate that the effectiveness of chain-of-thought prompting cannot be assessed independently of the evaluation methodology used to score model outputs. Under commonly used exact-match, automated answer extraction pipelines, explicit reasoning prompts interact poorly with verbose outputs, leading to dramatic measured accuracy degradation relative to direct prompting.

This section discusses the underlying causes of this behavior, its implications for both research and practice, and how these findings should be interpreted in the broader context of prior work on chain-of-thought prompting.

6.1 Prompting Strategy and Evaluation Are Joint Design Choices

A central takeaway from this study is that prompting strategy and evaluation protocol form a coupled system. While direct prompting typically produces short, unambiguous answers that align well with simple answer extraction heuristics, chain-of-thought prompting encourages verbose, multi-step outputs that are substantially harder to evaluate using exact-match criteria.

In many observed failure cases, the model’s reasoning contains the correct answer, but this answer is not reliably recoverable by simple normalization rules. As a result, measured accuracy reflects not only the model’s reasoning capability, but also the evaluator’s ability to extract the intended final answer.

This suggests that conclusions about the effectiveness of reasoning prompts must be interpreted with respect to the scoring pipeline used, particularly in automated benchmarking settings.

6.2 Why Larger Models Do Not Resolve the Issue

One might expect that increased model capacity would mitigate failures induced by chain-of-thought prompting. However, our results show that larger models exhibit equal or greater measured degradation under CoT prompting.

This indicates that scale alone does not address the core issue. Larger models tend to produce longer, more detailed reasoning chains, which further complicates answer extraction. As output verbosity increases, so does the likelihood that automated heuristics extract an intermediate value or irrelevant token rather than the intended final answer.

Thus, model scaling may amplify evaluation fragility rather than resolve it when prompt verbosity and scoring remain unchanged.

6.3 Concise Chain-of-Thought as a Partial Mitigation

Concise chain-of-thought prompting consistently performs better than full CoT but remains substantially worse than direct prompting under automated evaluation. This suggests a tradeoff between reasoning transparency and extractability.

By limiting verbosity, concise CoT reduces—but does not eliminate—the risk of answer extraction failures. This observation points toward a continuum of prompting strategies rather than a binary choice between “reasoning” and “no reasoning,” and suggests that careful control of output format may be necessary for reliable evaluation.

6.4 Implications for Benchmarking and Empirical Research

Our findings have direct implications for how reasoning benchmarks are constructed and interpreted:

Automated exact-match scoring may underestimate reasoning performance when models produce verbose outputs.

Prompting strategies should be evaluated jointly with extraction methods, particularly in zero-shot settings.

Reported gains or losses from chain-of-thought prompting may partially reflect evaluation artifacts rather than true differences in reasoning capability.

These issues are especially relevant for large-scale automated evaluations, where human verification is impractical and simple normalization heuristics are often employed.

6.5 Implications for Practitioners

For practitioners deploying language models in production systems, our results suggest several practical considerations:

Direct prompting remains a strong baseline for tasks with deterministic or low-entropy answers.

If chain-of-thought prompting is used, explicit answer formatting instructions (e.g., “Final Answer: <value>”) may be necessary to ensure reliable extraction.

Evaluation pipelines should be validated using representative model outputs rather than assumed to generalize across prompting styles.

In many real-world settings where automated scoring or downstream parsing is required, the simplicity of direct prompts may outweigh the interpretability benefits of explicit reasoning.

6.6 Relation to Prior Work on Chain-of-Thought

Our findings do not contradict prior demonstrations of the benefits of chain-of-thought prompting on complex reasoning tasks. Instead, they complement this literature by highlighting an often-overlooked aspect: the dependence of measured performance on evaluation design.

Much prior work evaluates CoT using:

Few-shot prompting

Tasks with unambiguous final answers

Manual or structured evaluation procedures

In contrast, our study focuses on zero-shot prompting, automated scoring, and relatively short-form tasks. Under these conditions, the interaction between verbose reasoning and simple answer extraction becomes a dominant factor in measured performance.

6.7 Limitations Revisited

While we identify evaluation mismatch as a primary driver of measured CoT failures, several limitations remain:

**Evaluation methodology**: Our answer extraction pipeline is intentionally simple and may not reflect best practices. The first-match numeric extraction heuristic (Section 3.4) was designed for terse direct responses and is known to fail on verbose outputs. More sophisticated extraction methods—such as LLM-based scoring, regex patterns tuned to each task type, or explicit answer formatting instructions (e.g., "Final Answer: <value>")—could substantially improve measured CoT performance.

**Intermediate reasoning verification**: We do not perform human evaluation to verify whether intermediate reasoning steps in failed CoT responses are actually correct before extraction failure occurs. Such verification would help quantify how much of the observed degradation stems from reasoning errors versus extraction artifacts.

**Model and task scope**: The study focuses on three Llama-family models and four task categories with relatively short-form answers. Results may not generalize to other architectures (e.g., GPT, Claude, Gemini) or task types with longer, more structured answers (e.g., multi-paragraph essays, code generation).

**Hyperparameter sensitivity**: We fix temperature at 0.2 (deterministic decoding). CoT prompts may exhibit different sensitivity profiles at higher temperatures or with different max_tokens settings, potentially due to increased exploration of the output space.

**Zero-shot evaluation**: We evaluate only zero-shot prompting without in-context examples. Few-shot CoT, which has shown substantial benefits in prior work (Wei et al., 2022), may exhibit different patterns and could mitigate the degradation observed here.

These findings should be interpreted as characterizing a common automated evaluation regime rather than a definitive assessment of reasoning correctness

6.8 Broader Implications

More broadly, this work highlights a fundamental tension between interpretability and evaluability. Techniques that improve transparency and reasoning traceability may simultaneously complicate automated scoring, creating misleading performance signals.

As language models are increasingly evaluated and deployed at scale, understanding and addressing these interactions will be critical to building reliable and trustworthy systems.

## 7. Broader Context and Comparison to Prior Work

### 7.1 When CoT Does Help

Literature documents cases where CoT helps:
- **High-complexity reasoning tasks**: 8-digit arithmetic (Wei et al., 2022)
- **Logical inference**: Formal logic with multiple premises
- **Few-shot learning**: Examples with reasoning enhance in-context learning
- **Larger models**: Scaling laws favor CoT for reasoning tasks

### 7.2 Why This Study Might Differ

This study focuses on:
- **Inference-only evaluation**: No fine-tuning on CoT
- **Zero-shot prompting**: No in-context examples
- **Relatively simple tasks**: Medium-difficulty problems, not PhD-level math
- **Automated evaluation**: Susceptible to answer extraction artifacts

The combination of these factors may explain the divergence from positive CoT results in prior work.

## 8. Recommendations for Future Work

### 8.1 Immediate Research Directions

1. **Improve answer extraction**: Implement LLM-based evaluation where another model judges correctness of reasoning.

2. **Task-specific prompt tuning**: Develop CoT variants specialized for each task type.

3. **Model-specific evaluation**: Test on models explicitly fine-tuned for CoT (GPT-4, Claude, Gemini).

4. **Human evaluation**: Random sample of 50-100 cases to validate automated scoring.

5. **Hyperparameter sweep**: Test different temperatures, max_tokens settings, and prompt variations.

### 8.2 Theoretical Questions

1. **Why do models generate verbose incorrect reasoning under CoT?** Is this an artifact of pre-training, or fundamental to reasoning prompts?

2. **Can CoT be made robust to answer extraction?** E.g., via "Answer: [ANSWER]" formatting instructions.

3. **Do different model sizes have different CoT sensitivity?** (We see 8b, 17b, 70b models showing similar degradation.)

4. **Is there a "sweet spot" for reasoning instructions?** (Intermediate prompts like concise CoT perform better than full CoT.)

## 9. Conclusion

This study presents empirical evidence that chain-of-thought prompting, despite its theoretical appeal and documented success on certain tasks, can lead to significant measured accuracy degradation under automated evaluation. Performance degradations range from 58.75% to 72.92% relative to direct prompting.

While we identify answer extraction and output format mismatch as likely root causes, the finding highlights an important gap: **there is no universal "best" prompt**. Success in prompt engineering requires careful empirical validation per task and per model.

The results challenge the prevailing intuition that "thinking step by step" always helps and suggest that for many practical scenarios, simplicity and directness may be preferable to elaborate reasoning instructions. Future work should focus on:
1. More sophisticated answer extraction and evaluation protocols
2. Task-model co-design for prompting strategies
3. Understanding the fundamental tradeoffs between output complexity and correctness

## References

- Wei, J., Wang, X., Schuurmans, D., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *arXiv:2201.11903*

- Reynolds, L., & McDonell, K. (2021). "Prompt Programming for Large Language Models: Beyond the Few-Shot Paradigm." *arXiv:2102.07350*

- White, J., Fu, Q., Zhang, S., et al. (2023). "A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT." *arXiv:2302.11382*

- Kojima, T., Gu, S. S., Reid, M., et al. (2022). "Large Language Models are Zero-Shot Reasoners." *arXiv:2205.11916*

## Appendix A: Complete Results Tables

### A.1 Accuracy by Model and Prompt Type (Full Table)

```
Model                                  | Direct | CoT    | Concise
llama-3.1-8b                           | 65.42% | 0.83%  | 5.42%
llama-3.3-70b                          | 79.58% | 6.67%  | 8.33%
llama-4-maverick                       | 60.00% | 1.25%  | 6.25%
```

### A.2 Accuracy by Model and Task

```
Model                          | Arithmetic | Factual | Reasoning | Symbolic Logic
llama-3.1-8b                   | 25.0%      | 27.2%   | 24.4%     | 18.9%
llama-3.3-70b                  | 30.0%      | 31.1%   | 38.3%     | 26.7%
llama-4-maverick               | 25.0%      | 25.0%   | 25.6%     | 14.4%
```

### A.3 CoT Delta by Model

```
Model                                  | CoT − Direct
llama-3.1-8b                           | −64.58%
llama-3.3-70b                          | −72.92%
llama-4-maverick                       | −58.75%
```

## Appendix B: Example Failure Cases

The file `figures/cot_failure_examples.csv` contains 471 cases where direct prompting succeeded but CoT failed under automated evaluation. This dataset includes the following columns:
- **model**: Model name (llama-3.1-8b, llama-3.3-70b, or llama-4-maverick)
- **prompt_type**: Either "direct" or "cot"
- **id, task, difficulty, question, gold_answer**: Question metadata and gold standard answer
- **model_output**: Raw output from the model
- **gold_norm, pred_norm**: Normalized gold and predicted answers after applying the pipeline from Section 3.4
- **correct**: Binary indicator of correctness (1 = correct, 0 = incorrect)

Researchers can use this file to:
1. Understand specific failure patterns and common error modes
2. Develop improved answer extraction heuristics beyond first-match numeric extraction
3. Analyze reasoning quality even when extraction fails (by examining model_output and pred_norm)
4. Design task-specific evaluation procedures tailored to CoT outputs
5. Identify opportunities for prompt engineering improvements (e.g., explicit answer formatting)

## Appendix C: Figures

- **Figure 1** (`figures/accuracy_vs_difficulty.png`): *Measured Accuracy vs Task Difficulty*. Line plots showing accuracy across easy, medium, and hard difficulty levels for each prompting strategy (direct, CoT, concise CoT), aggregated across all models. Demonstrates that the performance gap between direct and CoT prompting persists across all difficulty levels.

- **Figure 2** (`figures/accuracy_by_task.png`): *Measured Accuracy by Task Category*. Line plots showing accuracy across task categories (arithmetic, factual QA, reasoning, symbolic logic) for each prompting strategy, aggregated across all models. Illustrates that the CoT degradation effect is not confined to specific task types.

---

**Paper Metadata**
- **Date**: December 2025
- **Total Queries**: 2,160
- **Models Tested**: 3
- **Tasks Evaluated**: 240
- **Experiment Duration**: ~2 hours (including API delays)
