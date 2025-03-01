<h1 align="center">
  <b>InstA-gent 🤵‍♂️</b><br>
</h1>

This application allows any user to create agents with high-level reasoning capabiilties using only cheap, lightweight LLMs. We employ a meta-agent, inspired by Hu et al. [[7]](#7). Our meta-agent explores a possible design space and incorporates various inference-time reasoning techniques, such as Chain of Thought (CoT) [[2]](#2) or Reflexion [[3]](#3)

## Setup
```bash
conda create -n instagent python=3.11
conda activate instagent
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
 Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models," 2022,
arXiv:2201.11903.

<a id="2">[2]</a> Shinn et al. "Reflexion: Language Agents with Verbal Reinforcement Learning", 2023, arXiv:2303.11366.

<a id="3">[3]</a> Wang et al. "Self-Consistency Improves Chain of Thought Reasoning in Language Models", 2022, arXiv:2203.11171.

<a id="4">[4]</a> 
 S. Hu, C. Lu, and J. Clune, "Automated design of agentic systems," 2024,
arXiv:2408.08435.

<a id="5">[5]</a> 
Du et al. "Improving Factuality and Reasoning in Language Models through Multiagent Debate", 2023, arXiv:2305.14325.

<a id="6">[6]</a> 
Pugh, J. K., Soros, L. B., and Stanley, K. O. (2016). Quality diversity: A new frontier for evolutionary computation. Frontiers
in Robotics and AI, 3:40







