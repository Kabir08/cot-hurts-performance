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
FIG_DIR.mkdir(exist_ok=True)

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

    # extract numeric answers (ints / floats)
    numbers = re.findall(r"-?\d+\.?\d*", text)
    if numbers:
        return numbers[0]

    # remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# =========================
# LOAD
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
# SUMMARY TABLES
# =========================
print("\n=== Accuracy by Model × Prompt Type ===")
summary = (
    df.groupby(["model", "prompt_type"])["correct"]
    .mean()
    .reset_index()
    .sort_values(["model", "prompt_type"])
)
print(summary)

print("\n=== Accuracy by Model × Task ===")
task_summary = (
    df.groupby(["model", "task"])["correct"]
    .mean()
    .reset_index()
)
print(task_summary)

# =========================
# CoT DELTA TABLE
# =========================
pivot = (
    df.groupby(["model", "prompt_type"])["correct"]
    .mean()
    .unstack()
)

if "direct" in pivot.columns and "cot" in pivot.columns:
    pivot["cot_minus_direct"] = pivot["cot"] - pivot["direct"]

print("\n=== CoT − Direct Accuracy Delta ===")
print(pivot[["cot_minus_direct"]])

# =========================
# PLOT 1: Accuracy vs Difficulty
# =========================
difficulty_order = ["easy", "medium", "hard"]

diff_df = (
    df.groupby(["prompt_type", "difficulty"])["correct"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(7,5))
for ptype in diff_df["prompt_type"].unique():
    subset = diff_df[diff_df["prompt_type"] == ptype]
    subset["difficulty"] = pd.Categorical(
        subset["difficulty"],
        categories=difficulty_order,
        ordered=True
    )
    subset = subset.sort_values("difficulty")
    plt.plot(subset["difficulty"], subset["correct"], marker="o", label=ptype)

plt.xlabel("Difficulty")
plt.ylabel("Accuracy")
plt.title("Accuracy vs Difficulty")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(FIG_DIR / "accuracy_vs_difficulty.png")
plt.close()

print("[OK] Saved figures/accuracy_vs_difficulty.png")

# =========================
# PLOT 2: Task-wise Accuracy (Direct vs CoT)
# =========================
task_plot = (
    df.groupby(["task", "prompt_type"])["correct"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(8,5))
for ptype in ["direct", "cot", "concise_cot"]:
    subset = task_plot[task_plot["prompt_type"] == ptype]
    plt.plot(subset["task"], subset["correct"], marker="o", label=ptype)

plt.xlabel("Task")
plt.ylabel("Accuracy")
plt.title("Accuracy by Task")
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

if "direct" in failures.columns and "cot" in failures.columns:
    cot_failures = failures[
        (failures["direct"] == 1) &
        (failures["cot"] == 0)
    ]

    failure_examples = df.merge(
        cot_failures[["model", "id"]],
        on=["model", "id"]
    )

    failure_examples = failure_examples[
        failure_examples["prompt_type"].isin(["direct", "cot"])
    ]

    failure_examples.to_csv(FIG_DIR / "cot_failure_examples.csv", index=False)
    print("[OK] Saved figures/cot_failure_examples.csv")

print("\n=== DONE: Evaluation Complete ===")
