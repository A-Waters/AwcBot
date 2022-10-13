from time import sleep
from local_secrets import local_secrets

import requests
import re
sub_reddit="memes"

user_agent = {'User-agent': 'Mozilla/5.0'}
x = requests.get('https://old.reddit.com/r/'+sub_reddit+'/top/?sort=top&t=day', headers = user_agent)

code=x.text[x.text.find("thing id-t3")+12:x.text.find("thing id-t3")+18]

sleep(1)
x = requests.get('https://old.reddit.com/r/'+sub_reddit+'/comments/'+code+'/'+sub_reddit+'/', headers = user_agent)
link = x.text[x.text.find("post-link")-54:x.text.find("post-link")-19]


'''
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
'''