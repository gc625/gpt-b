import openai

openai.api_key = input()
response = openai.Completion.create(
    model='ada:ft-personal:gptb-2023-02-08-17-14-20',
    prompt='From the President: My Resignation',
    max_tokens=500)



with open('reponse2.txt','w') as f:
    f.write(response['choices'][0]['text'])

    f.close()

print(response['choices'][0]['text'])


