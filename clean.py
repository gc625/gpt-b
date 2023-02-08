import pickle
import json
import jsonlines
import re 
file = open("emails.pkl",'rb')
kathy_emails = pickle.load(file)
file.close()

no_dup = {}
def removeEnd(text):
    end = 'Katherine Bergeron*\r\nPresident'
    where_ellipsis = text.find(end)
    if where_ellipsis == -1:
        return text
    return text[:where_ellipsis + len(end)]

for k,v in kathy_emails.items():

    nobrac = re.sub("[\(\[].*?[\)\]]", "", v[1][0])
    no_dup[k] = [v[0],removeEnd(nobrac)]

    if len(v[1]) > 1: 
        print(v[1])
    # v[1] = v[1][0]
    # s += len(v[1])
    # print(len(v[1]))






print(len(kathy_emails), len(no_dup))

with open('output.jsonl', mode='w') as writer:
    
    for k,v in no_dup.items():

        text = {
            'prompt': v[0],
            'completion': v[1]
        }

        jsontext = json.dumps(text)
        writer.write(jsontext)
        writer.write('\n')

    writer.close()