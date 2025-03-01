<h1 align="center">
  <b>InstA-gent 🤵‍♂️</b><br>
</h1>

This application allows any user to create agents with high-level reasoning capabiilties using only cheap, lightweight LLMs. We employ a meta-agent, inspired by Hu et al. Our meta-agent explores a possible design space and incorporates various inference-time reasoning techniques, such as Chain of Thought (CoT) or Reflexion. 

## Setup
```bash
conda create -n instagent python=3.11
conda activate instagent
pip install -r requirements.txt

# provide your OpenAI API key
export OPENAI_API_KEY="YOUR KEY HERE"
```

See `api/README.md` for instructions on how to host a local LLAMA. Currently, our codebase is hard-coded to use this local LLAMA (but we have implemented functionality to use any OpenAI-compatible model API). 

## Running Instructions
```bash
python app.py
```

For a complete list of references, see [references.bib](references.bib).








