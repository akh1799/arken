import transformers
import torch
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import json

if os.path.exists('LOOKUP.JSON'):
    with open('LOOKUP.JSON', 'r') as f:
        LOOKUP = json.load(f)
else:
    LOOKUP={}

# Initialize FastAPI
app = FastAPI()

class LLAMAMODEL:
    _instance = None
    _lock = threading.Lock()  # Ensures only one instance is created

    def __new__(cls, model_id="/home/jovyan/api/meta-llama/Meta-Llama-3-8B-Instruct"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LLAMAMODEL, cls).__new__(cls)
                cls._instance._initialize(model_id)
        return cls._instance

    def _initialize(self, model_id):
        """Load the model only once."""
        self.model_id = model_id
        self.pipe = transformers.pipeline(
            "text-generation",
            model=model_id,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto"
        )
    def format_messages(self,messages):
        """Formats messages for LLama models."""
        formatted_prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                formatted_prompt += f"<<SYS>>\n{msg['content']}\n<</SYS>>\n\n"
            elif msg["role"] == "user":
                formatted_prompt += f"<|user|>\n{msg['content']}\n"
            elif msg["role"] == "assistant":
                formatted_prompt += f"<|assistant|>\n{msg['content']}\n"
        formatted_prompt += "<|assistant|>\n"  # Start of model response
        return formatted_prompt

    def query(self, messages, temperature=0.6, top_p=0.9, max_tokens=4096):
        """Generate response using the model."""
        if not messages or not isinstance(messages, list):
            raise ValueError("Messages must be a list of dictionaries.")
        
        user_prompt = self.format_messages(messages)  # Format messages correctly
        if user_prompt in LOOKUP:
            generated_text=LOOKUP[user_prompt]
        else:
            terminators = [
            self.pipe.tokenizer.eos_token_id,
            self.pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]
            # Generate response
            output = self.pipe(
                user_prompt,
                eos_token_id=terminators,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.6,
                top_p=0.9
            )
        
            # Extract generated text properly
            #generated_text = output[0]["generated_text"]
            generated_text = output[0]["generated_text"]
            LOOKUP[user_prompt]=generated_text
    
        response = {
            "id": "cmpl-" + "".join(str(ord(c)) for c in user_prompt[:5]),
            "object": "text_completion",
            "created": 1234567890,
            "model": self.model_id,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": generated_text},
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(user_prompt.split()) + len(generated_text.split())
            }
        }
        with open('LOOKUP.JSON', 'w') as f:
            json.dump(LOOKUP, f)
        return response

# Load model instance once
llama_model = LLAMAMODEL("/workspace/3BINSTRUCT")

# Define API Request Schema
class ChatRequest(BaseModel):
    messages: list
    temperature: float = 0.6
    top_p: float = 0.9
    max_tokens: int = 256

@app.post("/v1/chat/completions")
def chat(request: ChatRequest):
    """Handles API requests."""
    try:
        response = llama_model.query(
            messages=request.messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the API server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
