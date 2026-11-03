#!/bin/bash
# ==============================================================================
# NEUROTEACH AI — RunPod GPU Inference Worker Setup & Verification Script
# Executes on isolated Linux GPU instance (e.g. RTX A5000 24GB)
# STRICT SECURITY: No API keys, database credentials, or application code used.
# ==============================================================================
set -euo pipefail

echo "=== [1/5] Checking Hardware & GPU VRAM ==="
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader

echo "=== [2/5] Installing / Verifying Inference Environment ==="
# Install vllm or peft dependencies if not present
python3 -c "import torch; print('CUDA available:', torch.cuda.is_available(), 'Device:', torch.cuda.get_device_name(0))"
pip install -q "transformers>=4.49.0" "peft>=0.14.0" "safetensors>=0.4.3" "accelerate>=0.30.0" "fastapi" "uvicorn"

echo "=== [3/5] Verifying Checkpoint Artifacts ==="
CHECKPOINT_DIR="/workspace/adapter"
if [ ! -f "$CHECKPOINT_DIR/adapter_model.safetensors" ] || [ ! -f "$CHECKPOINT_DIR/adapter_config.json" ]; then
    echo "ERROR: Adapter files missing in $CHECKPOINT_DIR"
    exit 1
fi
echo "Adapter files verified in $CHECKPOINT_DIR"

echo "=== [4/5] Launching Secure Inference Server (Port 8000) ==="
# Launches a lightweight, standalone OpenAI-compatible server using PEFT and Hugging Face
cat << 'EOF' > /workspace/serve_adapter.py
import json
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import uvicorn

app = FastAPI(title="NeuroTeach Adapter Inference Server")

BASE_MODEL = "togethercomputer/Qwen3.5-4B"
ADAPTER_PATH = "/workspace/adapter"

print("Loading base model in bfloat16...")
tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
)
print("Loading PEFT LoRA adapter...")
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()
print("Model and adapter ready for inference!")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float = 0.2
    max_tokens: int = 512

@app.get("/health")
def health():
    return {"status": "ready", "model": "neuroteach-trained", "base": BASE_MODEL}

@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    # Format messages via tokenizer chat template
    text = tokenizer.apply_chat_template(
        [m.dict() for m in req.messages],
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature,
            do_sample=req.temperature > 0,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, outputs)
    ]
    response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return {
        "id": "chatcmpl-neuroteach",
        "object": "chat.completion",
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_text},
                "finish_reason": "stop",
            }
        ],
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

python3 /workspace/serve_adapter.py &
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

echo "=== [5/5] Waiting for Server Readiness ==="
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/health | grep -q "ready"; then
        echo "Server is ONLINE and READY!"
        break
    fi
    sleep 3
done

