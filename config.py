import openai
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
API_TOKEN = "6786447329:AAGBjuy7GKD1TK-mNYqkO8h2EgH3FNDdtPI"
ADMINS = [6139227440, 6977471553]


model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs.input_ids, max_length=200)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response