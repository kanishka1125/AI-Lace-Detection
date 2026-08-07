import torch
from transformers import AutoProcessor, AutoModelForCausalLM

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Using device: {device}")

MODEL_NAME = "microsoft/Florence-2-base"

print("Loading processor...")

processor = AutoProcessor.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("Loading Florence-2 model...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
).to(device)

model.eval()

print("✅ Florence-2 loaded successfully!")