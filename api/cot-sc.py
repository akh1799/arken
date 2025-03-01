import csv
import re
from collections import Counter
import transformers
import torch
import re

model_id = "meta-llama/Llama-3.1-8B-Instruct"

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
        prompt = f"""Question (Subject: {subject}):
{question_text}

Choices:
A) {choiceA}
B) {choiceB}
C) {choiceC}
D) {choiceD}

Provide a detailed, step-by-step chain of thought to reason about the correct choice (DO NOT exceed 60 tokens of reasoning).
Then finalize your answer at the end in the exact format:

Answer: X

(where X is one of A, B, C, or D, with no extra text).
"""

        N = 5 
        answers = [] 

        for _ in range(N):
            output = pipe(
                prompt,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.4,
                top_p=0.9
            )
            generated_text = output[0]["generated_text"]
            match = re.search(r"Answer:\s*([ABCD])", generated_text, re.IGNORECASE)
            if match:
                model_choice = match.group(1).upper()
                answers.append(model_choice)
            else:
                model_choice = "No clear choice"

        if answers:
            counter = Counter(answers)
            consensus_answer, consensus_count = counter.most_common(1)[0] 

            final_answer = consensus_answer

            num_questions += 1

            if final_answer == correct_ans:
                num_correct += 1
                is_correct_str = "CORRECT"
            else:
                is_correct_str = "WRONG"
    
            print(f"Question #{idx} (Subject: {subject})")
            print("Prompt:")
            print(prompt)
            print(f"All answers from {N} runs: {answers}")
            print(f"Consensus Answer: {final_answer}")
            print(f"Correct Answer: {correct_ans} => {is_correct_str}")
            print("-" * 70, "\n")

accuracy = 100.0 * num_correct / num_questions if num_questions else 0
print(f"Evaluated {num_questions} questions.")
print(f"Model got {num_correct} correct.")
print(f"Accuracy: {accuracy:.2f}%")
