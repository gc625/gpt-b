from __future__ import print_function

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path
import base64
import pickle
import time
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://mail.google.com/','https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.addons.current.message.readonly', 'https://www.googleapis.com/auth/gmail.addons.current.message.action']

def show_chatty_threads():
    """Display threads with long conversations(>= 3 messages)
    Return: None

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    # creds, _ = google.auth.default()

    # creds,_ = google.auth.load_credentials_from_file('credentials.json')


    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json()) 

    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)

        # pylint: disable=maybe-no-member
        # pylint: disable:R1710
        # threads = service.users().threads().list(userId='me').execute().get('threads', [])


        pageToken = '10501113621566398537'
        M = 500
        kathy_emails = {}
        file = open("emails.pkl",'rb')
        kathy_emails = pickle.load(file)
        file.close()


        for i in range(M):
            results = service.users().messages().list(userId='me',pageToken=pageToken).execute()
            message_ids = results.get('messages', [])

            messages = []


            def add(id, msg, err):
                # id is given because this will not be called in the same order
                if err:
                    print(err)
                else:
                    header_data = msg['payload']['headers']

                    for values in header_data:
                        if values["name"] == 'From' and values['value'] == 'Katherine Bergeron <president@conncoll.edu>':

                            subject = [j["value"] for j in header_data if j["name"] == "Subject"]
                            body = []
                            for p in msg["payload"]["parts"]:
                                
                                if p["mimeType"] in ['multipart/alternative']:
                                    for subp in p['parts']:
                                        if subp["mimeType"] in ["text/plain"]:
                                            data = base64.urlsafe_b64decode(subp["body"]["data"]).decode("utf-8")
                                        body += [data]

                                elif p["mimeType"] in ["text/plain"]:
                                    data = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")
                            body += [data]
                            kathy_emails[msg['id']] = (subject,body)
                    messages.append(msg)

            batch = service.new_batch_http_request()
            for msg in message_ids:
                batch.add(service.users().messages().get(userId='me', id=msg['id'],format='full'), add)
            batch.execute()

            pageToken = results['nextPageToken']
            print(f'num emails {len(kathy_emails)},i={i}')

            if i %30 == 0 and i > 0 :
                print('sleeping for 30 sec')
                time.sleep(30)

            filehandler = open("emails.pkl","wb")
            pickle.dump(kathy_emails,filehandler)
            filehandler.close()
        # for thread in threads:
        #     tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
        #     nmsgs = len(tdata['messages'])

        #     # skip if <3 msgs in thread
        #     if nmsgs > 2:
        #         msg = tdata['messages'][0]['payload']
        #         subject = ''
        #         for header in msg['headers']:
        #             if header['name'] == 'Subject':
        #                 subject = header['value']
        #                 break
        #         if subject:  # skip if no Subject line
        #             print(F'- {subject}, {nmsgs}')
        # return threads

    except HttpError as error:
        print(F'An error occurred: {error}')

        print(f'page token: {pageToken}')
        filehandler = open("emails.pkl","wb")
        pickle.dump(kathy_emails,filehandler)
        filehandler.close()


if __name__ == '__main__':
    show_chatty_threads()