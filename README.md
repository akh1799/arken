<h1 align="center">
  <b>One-Click Agents</b><br>
</h1>

This application allows any user to create agents with high-level reasoning capabiilties using only cheap, lightweight LLMs. We employ a meta-agent, inspired by Hu et al. [[1]](#1). Our meta-agent explores a possible design space and incorporates various inference-time reasoning techniques, such as Chain of Thought (CoT) [[2]](#2) or Reflexion [[3]](#3)

## Setup
```bash
conda create -n oneclickagents python=3.11
conda activate oneclickagents
pip install -r requirements.txt

# provide your OpenAI API key
export OPENAI_API_KEY="YOUR KEY HERE"
```

## Running Instructions
```bash
python gui.py
```

## References
<a id="1">[1]</a> 
 S. Hu, C. Lu, and J. Clune, "Automated design of agentic systems," 2024,
arXiv:2408.08435.

<a id="2">[2]</a> 
 Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models," 2022,
arXiv:2201.11903.


<a id="3">[3]</a> Shinn et al. "Reflexion: Language Agents with Verbal Reinforcement Learning"



