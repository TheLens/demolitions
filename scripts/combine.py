# -*- coding: utf-8 -*-

'''
Combines the photos and stories JSON files into a single JSON file that is
used to render the backend templates and define the front end data.
'''

import json
from slugify import slugify
from scripts.geocode import Geocode
from scripts import PROJECT_DIR


class Combine(object):

    '''Create master JSON file and trimmed version for front-end.'''

    def __init__(self):
        print '\nCombining JSON files...'

        self.photos_json = '%s/data/intermediate/photos.json' % PROJECT_DIR
        self.stories_json = '%s/data/intermediate/docs.json' % PROJECT_DIR

        self.combined_json = '%s/data/app/complete.json' % PROJECT_DIR
        self.reduced_json = '%s/data/app/reduced.json' % PROJECT_DIR

        self.photo_data = self._read_photos_json()
        self.story_data = self._read_stories_json()

        combined_json = self._combine_json_files()
        self._write_out_combined(combined_json)

        reduced_json = self._reduce_for_frontend()
        self._write_out_reduced(reduced_json)

    def _read_photos_json(self):
        '''doc'''

        with open(self.photos_json, 'r') as read_json:
            photo_data = json.load(read_json)

        return photo_data

    def _read_stories_json(self):
        '''doc'''

        with open(self.stories_json, 'r') as read_json:
            story_data = json.load(read_json)

        return story_data

    def _find_story(self, field, address):
        '''Looks for match between this photo address and story JSON.'''

        for story in self.story_data['stories']:
            if story['address'] == address:
                if field == 'story_type':
                    return 'story'
                else:
                    return story[field]

        # No matching story for these photos
        if field == 'story_type':
            return 'photo'
        else:  # body, head, subhead, byline, title
            return ''

    def _combine_json_files(self):
        '''Combines the two JSON files and returns a single JSON object.'''

        combined_json = {}
        combined_json['type'] = "FeatureCollection"

        features_list = []

        for location in self.photo_data['photos']:
            features_dict = {}
            features_dict['type'] = "Feature"

            address = location['address']

            geometry_dict = {}
            geometry_dict['type'] = "Point"
            geometry_dict['coordinates'] = Geocode(address)._geocode()
            features_dict['geometry'] = geometry_dict

            properties_dict = {}
            properties_dict['address'] = address

            properties_dict['slug'] = slugify(address)

            properties_dict['story_type'] = self._find_story(
                'story_type', address)
            properties_dict['title'] = self._find_story('title', address)
            properties_dict['head'] = self._find_story('head', address)
            properties_dict['subhead'] = self._find_story('subhead', address)
            properties_dict['byline'] = self._find_story('byline', address)
            properties_dict['body'] = self._find_story('body', address)

            # If photos only, make headline equal to address
            if properties_dict['head'] == '':
                properties_dict['head'] == address

            photos_list = []
            for photo_dict in location['photos']:
                photos_list.append(photo_dict)
            properties_dict['photos'] = photos_list

            features_dict['properties'] = properties_dict

            features_list.append(features_dict)

        combined_json['features'] = features_list

        return combined_json

    def _write_out_combined(self, output_json):
        with open(self.combined_json, 'w') as output:
            json.dump(output_json, output)

    def _reduce_for_frontend(self):
        '''
        Trims the comprehensive JSON down to only the parts necessary for the
        front end.
        '''

        output_json = {}

        with open(self.combined_json, 'rb') as fl:
            data = json.load(fl)

            output_json['type'] = data['type']
            features = []

            for feature in data['features']:
                features_dict = {}
                features_dict['type'] = feature['type']
                features_dict['geometry'] = feature['geometry']

                properties = feature['properties']

                properties_dict = {}
                properties_dict['story_type'] = properties['story_type']
                properties_dict['slug'] = properties['slug']
                properties_dict['address'] = properties['address']
                properties_dict['photos'] = properties['photos']

                features_dict['properties'] = properties_dict

                features.append(features_dict)

            output_json['features'] = features

        return output_json

    def _write_out_reduced(self, output_json):
        with open(self.reduced_json, 'w') as output:
            json.dump(output_json, output)

if __name__ == '__main__':
    Combine()
