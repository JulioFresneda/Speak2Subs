#from llama_cpp import Llama

def powerup_with_llama(string):
    # Put the location of to the GGUF model that you've download from HuggingFace here
    model_path = "/home/juliofgx/llama/llama-2-13b-chat.Q5_K_M.gguf"
    # Create a llama model
    #model = Llama(model_path=model_path)

    # Prompt creation
    system_message = ("Eres una maquina que corrije frases. El usuario te dirá una frase, y tú te tienes que limitar a corregirla. Necesitará, la frase corregida, literalmente entre caracteres '#'."
                      "Por ejemplo, si el usuario te dice: 'Bueno dias', tendrás que responder: '#Buenos días#'.")
    user_message = string

    prompt = f"""<s>[INST] <<SYS>>
    {system_message}
    <</SYS>>
    {user_message} [/INST]"""

    # Model parameters
    max_tokens = 100

    # Run the model
    #output = model(prompt, max_tokens=max_tokens, echo=True)

    # Print the model output
    #powered = output['choices'][0]['text']
    #print(powered)

    # Finding indices of '[' and ']'
    #start_index = powered.find('#')
    #end_index = powered.find('#')

    # Extracting substring between '[' and ']'
    #powered = powered[start_index + 1:end_index]
    #return powered


