import pandas as pd
import re
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# CONFIG
# =========================
INPUT_FILE = "results.csv"
OUTPUT_FILE = "scored_results.csv"

FIG_DIR = Path("figures")
TABLE_DIR = Path("tables")

FIG_DIR.mkdir(exist_ok=True)
TABLE_DIR.mkdir(exist_ok=True)

# =========================
# NORMALIZATION
# =========================
def normalize(text):
    if pd.isna(text):
        return ""

    text = str(text).lower().strip()

    # yes / no normalization
    if text.startswith("yes"):
        return "yes"
    if text.startswith("no"):
        return "no"

    # numeric extraction (first match only)
    numbers = re.findall(r"-?\d+\.?\d*", text)
    if numbers:
        return numbers[0]

    # remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_FILE)

# =========================
# NORMALIZE + SCORE
# =========================
df["gold_norm"] = df["gold_answer"].apply(normalize)
df["pred_norm"] = df["model_output"].apply(normalize)
df["correct"] = (df["gold_norm"] == df["pred_norm"]).astype(int)

df.to_csv(OUTPUT_FILE, index=False)
print(f"[OK] Scored results written to {OUTPUT_FILE}")

# =========================
# SUMMARY TABLES → FILES
# =========================

# Accuracy by model × prompt type
accuracy_model_prompt = (
    df.groupby(["model", "prompt_type"])["correct"]
      .mean()
      .reset_index()
      .sort_values(["model", "prompt_type"])
)

accuracy_model_prompt.to_csv(
    TABLE_DIR / "accuracy_by_model_prompt.csv",
    index=False
)

# Accuracy by model × task
accuracy_model_task = (
    df.groupby(["model", "task"])["correct"]
      .mean()
      .reset_index()
)

accuracy_model_task.to_csv(
    TABLE_DIR / "accuracy_by_model_task.csv",
    index=False
)

# CoT − Direct delta by model
pivot = (
    df.groupby(["model", "prompt_type"])["correct"]
      .mean()
      .unstack()
)

if {"direct", "cot"}.issubset(pivot.columns):
    pivot["cot_minus_direct"] = pivot["cot"] - pivot["direct"]

cot_delta = pivot[["cot_minus_direct"]].reset_index()

cot_delta.to_csv(
    TABLE_DIR / "cot_delta_by_model.csv",
    index=False
)

print("[OK] Saved summary tables to /tables/")

# =========================
# ERROR COUNTS (IMPORTANT)
# =========================

# Total / correct / incorrect by model × prompt
counts_model_prompt = (
    df.groupby(["model", "prompt_type"])["correct"]
      .agg(
          total="count",
          correct="sum"
      )
      .reset_index()
)

counts_model_prompt["incorrect"] = (
    counts_model_prompt["total"] - counts_model_prompt["correct"]
)

counts_model_prompt.to_csv(
    TABLE_DIR / "counts_by_model_prompt.csv",
    index=False
)

print("[OK] Saved tables/counts_by_model_prompt.csv")

# =========================
# PLOT 1: Accuracy vs Difficulty
# =========================
difficulty_order = ["easy", "medium", "hard"]

diff_df = (
    df.groupby(["prompt_type", "difficulty"])["correct"]
      .mean()
      .reset_index()
)

plt.figure(figsize=(7, 5))
for ptype in diff_df["prompt_type"].unique():
    subset = diff_df[diff_df["prompt_type"] == ptype].copy()
    subset["difficulty"] = pd.Categorical(
        subset["difficulty"],
        categories=difficulty_order,
        ordered=True
    )
    subset = subset.sort_values("difficulty")
    plt.plot(
        subset["difficulty"],
        subset["correct"],
        marker="o",
        label=ptype
    )

plt.xlabel("Difficulty")
plt.ylabel("Accuracy")
plt.title("Accuracy vs Difficulty (Aggregated Across Models)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(FIG_DIR / "accuracy_vs_difficulty.png")
plt.close()

print("[OK] Saved figures/accuracy_vs_difficulty.png")

# =========================
# PLOT 2: Accuracy by Task
# =========================
task_plot = (
    df.groupby(["task", "prompt_type"])["correct"]
      .mean()
      .reset_index()
)

plt.figure(figsize=(8, 5))
for ptype in ["direct", "cot", "concise_cot"]:
    subset = task_plot[task_plot["prompt_type"] == ptype]
    plt.plot(
        subset["task"],
        subset["correct"],
        marker="o",
        label=ptype
    )

plt.xlabel("Task")
plt.ylabel("Accuracy")
plt.title("Accuracy by Task (Aggregated Across Models)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(FIG_DIR / "accuracy_by_task.png")
plt.close()

print("[OK] Saved figures/accuracy_by_task.png")

# =========================
# FAILURE CASES (Direct ✓, CoT ✗)
# =========================
failures = df.pivot_table(
    index=["model", "id"],
    columns="prompt_type",
    values="correct"
).reset_index()

if {"direct", "cot"}.issubset(failures.columns):
    cot_failures = failures[
        (failures["direct"] == 1) &
        (failures["cot"] == 0)
    ]

    # Save failure examples
    failure_examples = df.merge(
        cot_failures[["model", "id"]],
        on=["model", "id"]
    )

    failure_examples = failure_examples[
        failure_examples["prompt_type"].isin(["direct", "cot"])
    ]

    failure_examples.to_csv(
        FIG_DIR / "cot_failure_examples.csv",
        index=False
    )

    print("[OK] Saved figures/cot_failure_examples.csv")

    # =========================
    # CoT FAILURE COUNTS (PAPER NUMBER)
    # =========================
    cot_failure_count = len(cot_failures)

    with open(TABLE_DIR / "cot_failure_count.txt", "w") as f:
        f.write(str(cot_failure_count))

    print(f"[OK] CoT failure count: {cot_failure_count}")

    # CoT failures by model
    cot_failures_by_model = (
        cot_failures.groupby("model")
                    .size()
                    .reset_index(name="cot_failure_count")
    )

    cot_failures_by_model.to_csv(
        TABLE_DIR / "cot_failures_by_model.csv",
        index=False
    )

    print("[OK] Saved tables/cot_failures_by_model.csv")

print("\n=== DONE: Evaluation Complete ===")
