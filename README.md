# dl-gdocs

Downloads or backups Google Documents (texts, spreadsheets, presentations). Useful if you want to get your stuff out of Google.

First install the required dependencies:

```
aptitude install python3-oauth2client
aptitude install python-httplib2
aptitude install python-jsonpath-rw
```

Then run:

```
python dl-gdocs.py
```
Notes:

* downloads Google text documents in the OpenDocument format ODT (LibreOffice/OpenOffice ) 
* downloads Google spreadsheets (Google Sheets) as Microsoft XLSX (no support for ODS) 
* downloads Google presentations (Google Slides)  as Microsoft PPTX (no support for ODP) 

Resources:

* Google Drive API: <https://developers.google.com/drive/web/about-sdk>
* <http://googleappsdeveloper.blogspot.fr/2012/08/exporting-native-google-documents-with.html>
