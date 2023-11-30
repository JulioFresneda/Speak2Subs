from openai import OpenAI

client = OpenAI(api_key="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")

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[{"role": "system", "content": "Say this is a test!"}],
  temperature=0,
  max_tokens=256,
)
print(response)