from openai import OpenAI


class GPT:
  def __init__(self):
    self.client = OpenAI(api_key="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")
    self.first_petition = ("Te voy a enviar una lista de frases, y necesito que corrijas la ortografía y sintaxis, añadiendo comas, tildes, y asegurándote de que los tiempos verbales tienen coherencia.")

    response = self.client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "system", "content": self.first_petition}],
      temperature=0,
      max_tokens=256,
    )
    self.first_reply = response.choices[0].message.content

  def fix_sentence(self, sentence):
    response = self.client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
          {"role": "system", "content": self.first_petition},
          {"role": "assistant", "content": self.first_reply},
          {"role": "user", "content": sentence}],
      temperature=0,
      max_tokens=256,
    )
    return response.choices[0].message.content



















