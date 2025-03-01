import csv
import re
import transformers
import torch
import re

model_id = "meta-llama/Llama-3.1-8B"

pipe = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto"
)

filename = "sample.txt"

num_questions = 0
num_correct = 0

with open(filename, mode="r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  

    for row in reader:
        idx = row[0].strip()
        question_text = row[1].strip()
        choiceA = row[2].strip()
        choiceB = row[3].strip()
        choiceC = row[4].strip()
        choiceD = row[5].strip()
        correct_ans = row[6].strip()
        subject = row[7].strip()

        num_questions += 1
        prompt = f"""Question (Subject: {subject}):
{question_text}

Choices:
A) {choiceA}
B) {choiceB}
C) {choiceC}
D) {choiceD}

Please select the single best answer (A, B, C, or D).
"""

        output = pipe(
            prompt,
            max_new_tokens=128,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

        generated_text = output[0]["generated_text"]

        match = re.search(r"\b([ABCD])\b", generated_text)

        if match:
            model_choice = match.group(1)
        else:
            model_choice = "No clear choice"

        if model_choice == correct_ans:
            num_correct += 1
            is_correct_str = "CORRECT"
        else:
            is_correct_str = "WRONG"

        print(f"Question #{idx} (Subject: {subject})")
        print(f"Prompt:\n{prompt}")
        print(f"Model output:\n{generated_text}")
        print(f"Model predicted: {model_choice} | Correct: {correct_ans} => {is_correct_str}")
        print("-" * 70, "\n")

accuracy = 100.0 * num_correct / num_questions if num_questions else 0
print(f"Evaluated {num_questions} questions.")
print(f"Model got {num_correct} correct.")
print(f"Accuracy: {accuracy:.2f}%")
