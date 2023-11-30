from transformers import AutoModelForCausalLM, AutoTokenizer




tokenizer = AutoTokenizer.from_pretrained("stabilityai/stablelm-base-alpha-3b-v2")
model = AutoModelForCausalLM.from_pretrained(
  "stabilityai/stablelm-base-alpha-3b-v2",
  trust_remote_code=True,
  torch_dtype="auto",
)
model.cpu()
inputs = tokenizer("Necesito que corrijas la ortografia y sintaxis de la siguiente frase: Mea burro mucho", return_tensors="pt").to("cpu")
tokens = model.generate(
  **inputs,
  max_new_tokens=64,
  temperature=0.75,
  top_p=0.95,
  do_sample=True,
)
print(tokenizer.decode(tokens[0], skip_special_tokens=True))