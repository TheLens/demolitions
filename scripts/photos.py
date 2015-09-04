
'''Downloads Google Sheet and parses the CSV into a JSON file.'''

import os
import re
import csv
import json
import httplib2
import urllib
import oauth2client

from slugify import slugify

from apiclient import discovery
from oauth2client import client
from oauth2client import tools

from scripts import PROJECT_DIR
from scripts.process_images import process_images

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class Photo(object):

    def __init__(self,
                 sheet_id='1wnGautZ-9PiNeCx_4Mc8VXb39OoNFf42XrVsHwHtXwQ'):
        self.sheet_id = sheet_id
        self.photos_csv = '%s/data/intermediate/photos.csv' % PROJECT_DIR
        self.photos_json = '%s/data/intermediate/photos.json' % PROJECT_DIR

        self.service = self._build_service()

        self._download_csv()
        self._parse_csv()
        self._download_images()
        self._process_images()
        self._update_json_with_filenames()

    def _download_csv(self):
        '''Runs processes for downloading Google Sheets file as CSV.'''
        content = self._get_file_contents(self.service)
        self._write_csv(content)

    def _build_service(self):
        '''Builds the Google Drive API service.'''
        credentials = self._get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v2', http=http)

        return service

    def _get_file_contents(self, service):
        '''Accesses Google Drive API to download the Sheets file contents.'''
        fil = self.service.files().get(fileId=self.sheet_id).execute()

        download_url = fil['exportLinks']['text/csv']

        resp, content = self.service._http.request(download_url)

        return content

    def _write_csv(self, content):
        '''Passes URL to download.'''

        with open(self.photos_csv, 'w') as csv_output:
            csv_output.write(content)

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

    def _parse_csv(self):
        '''Runs processes to parse CSV and write out to JSON.'''

        photos_json = self._csv_to_json()
        self._write_json(photos_json)

    def _csv_to_json(self):
        '''Reads Google CSV and converts to JSON.'''

        with open(self.photos_csv, 'rb') as csv_in:
            csvreader = csv.reader(csv_in)
            next(csvreader)  # Skip header

            photo_json = {}
            photo_list = []

            address_dict = {}  # One per address
            address_photos_list = []  # List of photos for this address

            previous_address = ''

            num_rows = 325 - 1  # TODO: Remove magic number

            for i, row in enumerate(csvreader):
                this_photo_dict = {}

                this_address = row[0].strip()
                image_url = row[2]
                old_source = row[5]  # Use to identify FEMA/HNOC photos
                source = row[6]
                photographer = ''
                if '/' in source:
                    photographer = source.split('/')[0]
                else:
                    photographer = source
                date = row[10]
                caption = row[11]

                this_photo_dict['source'] = source
                this_photo_dict['old_source'] = old_source
                this_photo_dict['url'] = image_url
                this_photo_dict['photographer'] = photographer
                this_photo_dict['date'] = date
                this_photo_dict['caption'] = caption

                # To avoid trailing/leading blanks
                if this_address != previous_address and previous_address != '':
                    # New address, other than first row
                    # Write out address_list to address_dict, append
                    # address_dict to photos_list and create new and prep new
                    # one
                    address_dict['address'] = previous_address
                    address_dict['photos'] = address_photos_list

                    photo_list.append(address_dict)
                    address_dict = {}
                    address_photos_list = []

                address_photos_list.append(this_photo_dict)

                if i == num_rows:
                    address_dict['address'] = previous_address
                    address_dict['photos'] = address_photos_list

                    photo_list.append(address_dict)

                previous_address = this_address

            photo_json['photos'] = photo_list

            return photo_json

    def _download_images(self):
        '''Reads through photos JSON and downloads images.'''

        print '\nDownloading images...'

        # Store full images here. Scaled images will go in /static/images.
        images_dir = '%s/data/selected-photos' % PROJECT_DIR

        with open(self.photos_json, 'r') as read_json:
            photo_data = json.load(read_json)

        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        for location in photo_data['photos']:
            location_folder = slugify(location['address'])
            location_dir = os.path.join(images_dir, location_folder)

            if not os.path.exists(location_dir):
                os.makedirs(location_dir)

            for i, photo in enumerate(location['photos']):
                # Save photo to new directory
                target = location_dir + '/%d.jpg' % (i + 1)

                url = photo['url']
                old_source = photo['old_source']

                print url

                if 'HNOC/FEMA' in old_source:  # To check for cropping
                    target = location_dir + '/%d-fema.jpg' % (i + 1)

                try:
                    if not os.path.isfile(target):  # Skip if file exists
                        if 'google' in url.lower():
                            image_id = ''
                            if 'open?' in url.lower():
                                # https://drive.google.com/open?id=0B6n8-hNi9AU2ZnRlUHdEN2lld3M
                                image_id = re.search(
                                    r'id\=(.*?)$', url).group(1)

                            if 'thelensnola' in url.lower():
                                # https://drive.google.com/a/thelensnola.
                                # org/file/d/0B2doKNlGQ8nJV3BlU1NSQVh6NFE/view
                                image_id = re.search(
                                    r'\/d\/(.*?)\/view', url).group(1)

                            fil = self.service.files().get(
                                fileId=image_id).execute()

                            download_url = fil['downloadUrl']
                            resp, content = self.service._http.request(
                                download_url)

                            with open(target, 'w') as jpeg_input:
                                jpeg_input.write(content)
                        else:
                            urllib.urlretrieve(url, target)
                except:
                    raise ValueError('No file found!')

    def _process_images(self):
        '''Crop, scale, make copies of images in /static/images.'''
        process_images()

    def _get_filename(self, i, slug, size_type):
        '''Find file name for this image.'''

        this_dir = '%s/demolitions/static/images/%s' % (PROJECT_DIR, slug)

        image_number = str(i + 1) + '-'

        file_list = os.listdir(this_dir)

        this_file_list = sorted(
            [f for f in file_list if '%s' % image_number in f])

        num_files_this_list = sum(
            1 for f in file_list if '%s' % image_number in f)

        if size_type == 'small':
            return this_file_list[-1]
        elif size_type == 'medium':
            return this_file_list[0]
        elif size_type == 'large':
            if num_files_this_list >= 3:
                return this_file_list[1]
            else:
                return this_file_list[0]
        elif size_type == 'xlarge':
            if num_files_this_list == 4:
                return this_file_list[2]
            elif num_files_this_list == 3:
                return this_file_list[1]
            else:
                return this_file_list[0]

    def _update_json_with_filenames(self):
        '''
        Reads through JSON and updates based on processed image filenames, both
        small and large sizes.
        '''

        with open(self.photos_json, 'r') as read_json:
            photo_data = json.load(read_json)

        for location in photo_data['photos']:
            slug = slugify(location['address'])

            for i, photo in enumerate(location['photos']):
                filename_dict = {}
                filename_dict['small'] = self._get_filename(i, slug, 'small')
                filename_dict['medium'] = self._get_filename(i, slug, 'medium')
                filename_dict['large'] = self._get_filename(i, slug, 'large')
                filename_dict['xlarge'] = self._get_filename(i, slug, 'xlarge')
                photo['filename'] = filename_dict

        # Write out JSON back into same file
        self._write_json(photo_data)

    def _write_json(self, out_json):
        '''Write JSON out to a file.'''

        with open(self.photos_json, 'w') as output:
            json.dump(out_json, output)

if __name__ == '__main__':
    Photo()
