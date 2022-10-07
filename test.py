from local_secrets import local_secrets
import openai

openai.api_key = local_secrets['openai']

engines = openai.Engine.list()



completion = openai.Completion.create(engine="text-ada-001",
    prompt="Human:Hello\n Ai:", 
    temperature=0.9,
    max_tokens=25,
    presence_penalty=0.6,
    frequency_penalty=0.1
    )

print(completion.choices[0].text)