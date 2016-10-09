#!/usr/bin/env python

"""
sample python script for using Clarifai Python Client API

usage: sample_main.py [-h] [-t] [-c]

optional arguments:
  -h, --help   show this help message and exit
  -t, --tag    tag images
  -c, --color  color images

Examples:

Run tag api on an image url or image on disk
 python sample_main.py <url|filename>
 python sample_main.py -t|--tag <url|filename>

Run color api on an image url or image on disk
 python sample_main.py -c|--color <url|filename>

"""
from __future__ import print_function

import os
import sys
import json
import glob
import argparse
import subprocess
import cv2
from pprint import pprint

from clarifai.client import ClarifaiApi

import httplib2
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from apiclient import errors

def tag_images(api, imageurl):
  if imageurl.startswith('http'):
    response = api.tag_image_urls(imageurl)
  elif os.path.isfile(imageurl):
    with open(imageurl,'rb') as image_file:
      response = api.tag_images(image_file)

  return response

def color_images(api, imageurl):
  if imageurl.startswith('http'):
    response = api.color_urls(imageurl)
  elif os.path.isfile(imageurl):
    with open(imageurl,'rb') as image_file:
      response = api.color(image_file)

  return response


def main(argv):

  # parse arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--tag", help="tag images", action='store_true')
  parser.add_argument("-c", "--color", help="color images", action='store_true')
  parser.add_argument("-u", "--usage", help="usage", action='store_true')

  args, argv = parser.parse_known_args()

  if len(argv) == 1:
    imageurl = argv[0]
  else:
    cmd = ["curl", "-v", "-L", "-H"]
    cmd.append("""Content-Type: application/json""")
    cmd.append("-H")
    cmd.append("""Authorization: Bearer c.8jSn8pe6vsvCznvGIh5kuGfzouV7ZUgcwSldh4F9e8fZ6vrPqYxNSpzOzwgTErEqYS2F6cDeTcY0VmfMpqZJ5MXBFQpMeh7BZBwTi3xmZUDNTg4dfuX09unqCesVpuKdqxUhfhPgWGJE616I""")
    cmd.append("-X")
    cmd.append("GET")
    cmd.append("""https://developer-api.nest.com/devices/cameras/""")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()
    if p.returncode is not 0:
        print("Failed to execute command: %s" % (' '.join(cmd)))
    url_json = json.loads(output[0].decode('utf-8'))
    url = url_json["HVnTMdqBL607L2Ty14rgiZSHzyu3knTnlRAAGaz_Et2y9LBGS4OTrg"]["snapshot_url"]
    cmd = ["curl", "-o", "image.jpg", "-O", url]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0]
    if p.returncode is not 0:
        print("Failed to execute command: %s" % (' '.join(cmd)))
    imageurl = 'image.jpg'

  api = ClarifaiApi()

  if args.usage:
    response = api.get_usage()
  elif not args.color:
    response = tag_images(api, imageurl)
  elif args.color and not args.tag:
    response = color_images(api, imageurl)
  else:
    print("Error")
    raise Exception('call with --tag or --color for the image')


  #print(json.dumps(response))
  #https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file-in-python
  with open('data.txt', 'w') as outfile:
    json.dump(response, outfile)
  #pprint(response)
  relevant_response = response['results'][0]['result']['tag']
  #for cls in response['results'][0]['result']['tag']['classes'] and prob in response['results'][0]['result']['tag']['probs']:
  man = False
  woman = False
  woman_prob = 0.80
  man_prob = 0.80
  for cls, prob in zip(relevant_response['classes'], relevant_response['probs']):
    #print("Tag: ", cls,"\n\tProb: ", prob)
    print("Prob: ", prob, "\t\tTag: ", cls)
    if (cls == "man" and prob > man_prob) or (cls == "boy" and prob > man_prob):
        man = True
    if (cls == "woman" and prob > woman_prob) or (cls == "girl" and prob > woman_prob):
        if not man:
            woman = True

  #text_result = "No men or women found."
  if man:
    print("Found a man!")
    text_result="Found a man!"
  if woman:
    print("Found a woman!")
    text_result="Found a woman!"
  
  # If modifying these scopes, delete your previously saved credentials
  # at ~/.credentials/gmail-python-quickstart.json
  SCOPES = 'https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/gmail.send'
  CLIENT_SECRET_FILE = 'client_secret.json'
  APPLICATION_NAME = 'hackUstate'


  def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    #home_dir = os.path.expanduser('C:\Users\skyle')
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

#def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('gmail', 'v1', http=http)


  # service.users().messages().send(userId='me', "test message").execute()

  # results = service.users().labels().list(userId='me').execute()
  # labels = results.get('labels', [])

  # if not labels:
  #     print('No labels found.')
  # else:
  #   print('Labels:')
  #   for label in labels:
  #     print(label['name'])

  def SendMessage(service, user_id, message):
  # """Send an email message.

  # Args:
  #   service: Authorized Gmail API service instance.
  #   user_id: User's email address. The special value "me"
  #   can be used to indicate the authenticated user.
  #   message: Message to be sent.

  # Returns:
  #   Sent Message.
  # """
    #try:
    message = (service.users().messages().send(userId='me', body=message).execute())
    #print ('Message Id: %s' % message['id'])
    return message
    #except errors.HttpError, error:
      #print('An error occurred: %s' % error)


  def CreateMessage(sender, to, subject, message_text):
  # """Create a message for an email.

  # Args:
  #   sender: Email address of the sender.
  #   to: Email address of the receiver.
  #   subject: The subject of the email message.
  #   message_text: The text of the email message.

  # Returns:
  #   An object containing a base64url encoded email object.
  # """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(message_text)
    message.attach(msg)

    #path = os.path.join("C:\Users\skyle\hackustatecamera", "image.png")
    path = os.path.join("/home/kappa/clarifai-python", "image.jpg")
    content_type, encoding = mimetypes.guess_type(path)
    if content_type is None or encoding is not None:
      content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    fp = open(path, 'rb')
    msg = MIMEImage(fp.read(), _subtype=sub_type)
    fp.close()
    msg.add_header('Content-Disposition', 'attachment', filename="image.jpg")
    message.attach(msg)
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

  
  created = CreateMessage("security", "s.cowley@aggiemail.usu.edu","Camera Alert", text_result)
  SendMessage(service,'me',created)






if __name__ == '__main__':
  main(sys.argv)
