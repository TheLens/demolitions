# -*- coding: utf-8 -*-

'''Downloads Google Docs, parses contents and exports to JSON.'''

import os
import json
import httplib2
import archieml
import oauth2client

from scripts import PROJECT_DIR
from apiclient import discovery
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class Doc(object):

    def __init__(self, doc_ids):
        self.doc_ids = doc_ids

        self.docs_json = '%s/data/intermediate/docs.json' % PROJECT_DIR

        self._main()

    def _main(self):
        '''Downloads Google Doc contents and convert to JSON using ArchieML.'''

        print '\nDownloading docs...'

        total_json = {}
        stories_list = []

        service = self._build_service()

        for doc_id in self.doc_ids:
            contents = self._get_file_contents(
                service, doc_id)

            contents_json = archieml.loads(contents)

            contents_json = self._parse_plain_text_for_html(contents_json)

            stories_list.append(contents_json)

        total_json['stories'] = stories_list

        self._write_json(total_json)

    def _build_service(self):
        credentials = self._get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v2', http=http)

        return service

    def _get_file_contents(self, service, file_id):
        fil = service.files().get(fileId=file_id).execute()

        download_url = fil['exportLinks']['text/plain']

        resp, content = service._http.request(download_url)

        return content

    def _parse_plain_text_for_html(self, contents_json):
        '''
        Input is plain text, output is basic HTML with <p>
        tags and hyperlinks.
        '''

        body = contents_json['body']

        # End and start of paragraph
        body = body.replace('\r\n\r\n\r\n', '</p><p>')

        # Convert normal line breaks into spaces.
        body = body.replace('\r\n', ' ')

        # Decode to unocde, replace <a> tag quotes, encode
        body = body.decode('utf-8').replace(
            u'\u2019', "'").encode('utf-8')

        # Start and end of body
        body = '<p>' + body + '</p>'

        contents_json['body'] = body

        return contents_json

    def _write_json(self, out_json):
        '''Writes out JSON to file.'''

        with open(self.docs_json, 'w') as output:
            json.dump(out_json, output)

    def _get_credentials(self):
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """

        scopes = 'https://www.googleapis.com/auth/drive'
        client_secret_file = '%s/config/client_secret.json' % PROJECT_DIR
        application_name = 'Drive API Quickstart'

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)

        credential_path = os.path.join(credential_dir, 'drive-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(client_secret_file, scopes)
            flow.user_agent = application_name

            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatability with Python 2.6
                credentials = tools.run(flow, store)

        return credentials
