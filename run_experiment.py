import json
import csv
import time
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])


# ===== CONFIG =====
MODEL_LIST = [
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-maverick-17b-128e-instruct"
]

TEMPERATURE = 0.2
MAX_TOKENS = 256

PROMPTS = {
    "direct": "Answer the question directly.\nQuestion: {q}\nAnswer:",
    "cot": "Answer the question. Think step by step before answering.\nQuestion: {q}\nAnswer:",
    "concise_cot": "Answer the question. Give a brief explanation, then the answer.\nQuestion: {q}\nAnswer:"
}


# ===== LOAD DATA =====
with open("dataset.json") as f:
    dataset = json.load(f)

# ===== OUTPUT =====
output_file = "results.csv"
file_exists = os.path.isfile(output_file)

out_file = open(output_file, "a", newline="")
writer = csv.writer(out_file)
writer.writerow([
    "model", "prompt_type", "id", "task", "difficulty",
    "question", "gold_answer", "model_output"
])

# ===== RUN =====
for model in MODEL_LIST:
    for item in dataset:
        for ptype, template in PROMPTS.items():
            prompt = template.format(q=item["question"])

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )

            output = response.choices[0].message.content.strip()

            writer.writerow([
                model, ptype, item["id"], item["task"],
                item["difficulty"], item["question"],
                item["answer"], output
            ])

            time.sleep(0.1)  # polite pacing

out_file.close()
print("DONE.")
