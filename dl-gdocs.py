#!/usr/bin/python3
"""
Downloads all your Google documents (text, presentation, spreadsheets) 

You can leave a comment below

URL: https://github.com/monperrus/dl-gdocs/
Author: Martin Monperrus
Date: April 2015 (still working on Sep 2019)
Licence: MIT
"""

## CONSTANTS
# this file is created automatically
# if errors remove it: "rm google-credentials.json"
GOOGLE_CREDENTIALS_FILE = 'google-credentials-dl-gdocs.json'

# dependencies
import json
import httplib2
import re
import os
import iso8601
import datetime
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
import time  

def get_credential_oauth():
  """ returns a credential object from the Google OAuth webservice"""

  # the application id: 
  # if this one gets blocked (by Google or myself)
  # you may create your own at https://console.developers.google.com/
  # project dl-gdocs
  # credentials >> Create New Client ID >> Installed application >> Other
  client_secrets = json.loads(open('/home/martin/client_secret_879219052242-anuu8p1or7c3ju6hv7fu426vkk1rf27k.apps.googleusercontent.com.json').read())

  #  flow = flow_from_clientsecrets('google.json', scope='',  redirect_uri='urn:ietf:wg:oauth:2.0:oob')
  
  flow = OAuth2WebServerFlow(client_id=client_secrets["installed"]["client_id"],
                           client_secret=client_secrets["installed"]["client_secret"],
                           scope='https://www.googleapis.com/auth/drive',
                           redirect_uri='urn:ietf:wg:oauth:2.0:oob')
  

  auth_uri = flow.step1_get_authorize_url()

  print("Please go to this URL and get an authentication code:")
  print(auth_uri)

  print("Please input the authentication code here:")
  code = input("code?")
  credentials = flow.step2_exchange(code)
  storage = Storage(GOOGLE_CREDENTIALS_FILE)
  storage.put(credentials)
  return credentials

def get_credential():
  """ gets the correct credentials """
  if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
    return get_credential_oauth()    
  """ returns a credential object, first by trying the one on disk, second, by using the web-based Oauth system """
  storage = Storage(GOOGLE_CREDENTIALS_FILE)  
  credentials = storage.get()
  if credentials == None:
    return get_credential_oauth()    
  return credentials

def download_gdocs(doc_mime_type, export_mime_type):
  """downloads all Google documents with mime type given as parameter, export_mime_type is the  required export mime type """
  http = httplib2.Http()
  credentials = get_credential()
  http = credentials.authorize(http)
  content={"nextLink":"https://www.googleapis.com/drive/v2/files/?q=mimeType='"+doc_mime_type+"'"}
  i=0
  while "nextLink" in content:
    i+=1
    #if i>2: break # used for debug
    resp, content = http.request(content["nextLink"], "GET")
    content = json.loads(content)
    items = content['items']
    # formatted RFC 3339 timestamp
    for item in items:
        mdate = iso8601.parse_date(item['modifiedDate'])
        delta = datetime.datetime.today()-mdate.replace(tzinfo=None)
        if delta.days < 720: # only download the recently modified files
            # download it
            link = item['exportLinks'][export_mime_type]
            # changes in item.keys()
            print(delta, link)
            download_file(link, time.mktime(mdate.timetuple()))

    
def download_file(export_url, modTime = 0):
  """ downloads the google document from this export URL.
  uses the file name given in the content-disposition HTTP header"""
  #print url
  #continue
  http = httplib2.Http()
  credentials = get_credential()
  http = credentials.authorize(http)
  resp, content = http.request(export_url, "GET")    
  # If the response has Content-Disposition, we take filename from it
  # print resp['content-disposition']
  match = re.match('.*"(.*?)".*', resp['content-disposition'])
  name = match.group(1)
  if (len(name)>140): name = name[:-140]
  print("downloading",name)
  with open(name, 'wb') as f:
    f.write(content)
    os.utime(name, (modTime, modTime))

# for a list of Google Documents mime type, see https://developers.google.com/drive/web/mime-types
# for opendocument mime types, see http://en.wikipedia.org/wiki/OpenDocument_technical_specification

# downloads Google text documents in the OpenDocument format ODT (LibreOffice/OpenOffice ) 
download_gdocs('application/vnd.google-apps.document', 'application/vnd.oasis.opendocument.text')

# downloads Google spreadsheets (Google Sheets) as Microsoft XLSX (no support for ODS) PDF is also possible
download_gdocs('application/vnd.google-apps.spreadsheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# downloads Google presentations (Google Slides)  as Microsoft PPTX (no support for ODP) PDF is also possible
download_gdocs('application/vnd.google-apps.presentation', 'application/vnd.openxmlformats-officedocument.presentationml.presentation')

