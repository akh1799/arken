import random
import string
from collections import namedtuple
import pandas as pd
import numpy as np

Example = namedtuple('Example', ['question', 'answer', 'additional_info'])

QUERY_TEMPLATE_GENERIC = """
{question_text}

{options_text}
""".strip()

def format_question(row, is_multiple_choice=True):
    """
    Format a question based on the row data and whether it's multiple choice.
    
    Args:
    - row (pd.Series): Row from the dataset
    - is_multiple_choice (bool): Whether the question is multiple choice
    
    Returns:
    - str: Formatted question
    - dict: Additional information from other columns
    """
    question_text = row['Question'] if 'Question' in row else row.iloc[0]
    answer = row['Answer'] if 'Answer' in row else row.iloc[1]
    
    # Get additional info from other columns
    additional_info = {col: row[col] for col in row.index 
                      if col not in ['Question', 'Answer']}
    
    if is_multiple_choice:
        # Try to find multiple choice options
        options = []
        option_cols = [col for col in row.index if col.startswith(('choice', 'option', 'Choice', 'Option'))]
        
        if option_cols:
            options_text = "\n".join(f"({chr(65+i)}) {row[col]}" for i, col in enumerate(option_cols))
        else:
            # If no explicit options found, try to parse the answer for options
            # Assuming options are in format (A) ... (B) ... etc.
            import re
            options_match = re.findall(r'\([A-D]\)[^(]*', str(answer))
            if options_match:
                options_text = "\n".join(opt.strip() for opt in options_match)
            else:
                # Default to treating answer as the correct option
                options_text = "(A) " + str(answer)
    else:
        options_text = ""
    
    formatted_question = QUERY_TEMPLATE_GENERIC.format(
        question_text=question_text,
        options_text=options_text
    )
    
    return formatted_question, additional_info

def load_dataset(file_path, is_multiple_choice=True):
    """
    Load a dataset from a CSV file.
    
    Args:
    - file_path (str): Path to the CSV file
    - is_multiple_choice (bool): Whether the questions are multiple choice
    
    Returns:
    - list: List of Example namedtuples
    """
    df = pd.read_csv(file_path)
    
    examples = []
    for _, row in df.iterrows():
        formatted_question, additional_info = format_question(row, is_multiple_choice)
        example = Example(
            question=formatted_question,
            answer=row['Answer'] if 'Answer' in row else row.iloc[1],
            additional_info=additional_info
        )
        examples.append(example)
    
    return examples

def random_id(length=4):
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choices(characters, k=length))
    return random_id

def bootstrap_confidence_interval(data, num_bootstrap_samples=100000, confidence_level=0.95):
    """
    Calculate the bootstrap confidence interval for the mean of 1D accuracy data.
    Also returns the median of the bootstrap means.
    
    Args:
    - data (list or array of float): 1D list or array of data points.
    - num_bootstrap_samples (int): Number of bootstrap samples.
    - confidence_level (float): The desired confidence level (e.g., 0.95 for 95%).
    
    Returns:
    - str: Formatted string with 95% confidence interval and median as percentages with one decimal place.
    """
    data = np.array(data)
    bootstrap_means = []

    for _ in range(num_bootstrap_samples):
        bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_mean = np.mean(bootstrap_sample)
        bootstrap_means.append(bootstrap_mean)

    bootstrap_means = np.array(bootstrap_means)
    lower_percentile = (1.0 - confidence_level) / 2.0
    upper_percentile = 1.0 - lower_percentile
    ci_lower = np.percentile(bootstrap_means, lower_percentile * 100)
    ci_upper = np.percentile(bootstrap_means, upper_percentile * 100)
    median = np.median(bootstrap_means)

    ci_lower_percent = ci_lower * 100
    ci_upper_percent = ci_upper * 100
    median_percent = median * 100

    return f"95% Bootstrap Confidence Interval: ({ci_lower_percent:.1f}%, {ci_upper_percent:.1f}%), Median: {median_percent:.1f}%"
