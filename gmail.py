
from __future__ import print_function
import httplib2
import os
import base64
import email

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def parseRawMsg(msg):
    """
    Parse the raw message.
    :param msg: raw message
    :return: from, subject, body
    """
    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    msg_parsed = email.message_from_string(msg_str.decode("utf-8"))

    b = msg_parsed
    if b.is_multipart():
        for part in b.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = b.get_payload(decode=True)
    # print('Body:', body.decode("utf-8"))

    body = body.decode("utf-8").lower()
    return msg_parsed['from'].lower(), msg_parsed['subject'].lower(), body


def archiveMsg(service, user_id, msg_id):
    """
    Archive emails by removing the 'INBOX' label
    :return:
    """
    # TODO: Add dedicated label?
    newLabels = {'removeLabelIds': ['INBOX'], 'addLabelIds': []}
    service.users().messages().modify(userId=user_id, id=msg_id, body=newLabels).execute()


def parseMsgInfo(msg_from, msg_sbj, msg_bdy):
    """
    Extract the info from message.
    TODO: Store the extracted data.
    """
    msg_txt = msg_sbj + ' ' + msg_bdy

    isProf = False
    if 'professor' in msg_txt or 'instructor' in msg_txt:
        isProf = True

    isGradStudent = False
    if 'student' in msg_txt or 'post doctoral' in msg_txt:
        isGradStudent = True

    print('isProf', isProf)
    print('isGradStudent', isGradStudent)
    print('-----------------')


def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    user_id = 'me'
    label_ids = [
        'INBOX',
        'CATEGORY_PERSONAL',
                 ]
    results = service.users().messages().list(userId=user_id, labelIds=label_ids).execute()

    for msgId in results['messages'][:5]:
        msg_id = msgId['id']
        msg = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_from, msg_sbj, msg_bdy = parseRawMsg(msg)
        print('from:', msg_from)
        print('subject:', msg_sbj)

        parseMsgInfo(msg_from, msg_sbj, msg_bdy)

        # Archive the message TODO: Enable when ready!!!
        # archiveMsg(service, user_id, msg_id)

if __name__ == '__main__':
    main()
