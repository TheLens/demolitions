# -*- coding: utf-8 -*-

'''Takes project data JSON and renders HTML.'''

import json
from jinja2 import (
    Environment,
    FileSystemLoader
)
from subprocess import call
from scripts import (
    PROJECT_DIR,
    DEMOLITIONS_CSS,
    DEMOLITIONS_JS,
    EVENT_TRACKING_JS,
    RENDER_DEMOLITIONS_CSS,
    RENDER_DEMOLITIONS_JS,
    RENDER_EVENT_TRACKING_JS
)


class Render(object):

    def __init__(self):
        '''docstring'''

        print '\nRendering HTML...'

        self.render_development_html('index')
        self.render_development_html('nation')
        self.render_production_html('index')
        self.render_production_html('nation')
        self.render_sass()

    def render_sass(self):
        '''Render SASS files.'''

        call([
            'sass',
            '%s/demolitions/static/css/scss/demolitions.scss' % PROJECT_DIR,
            '%s/demolitions/static/css/demolitions.css' % PROJECT_DIR
        ])

    def read_json(self):
        '''Read HTML files for passing to render function.'''

        json_file = '%s/data/app/complete.json' % PROJECT_DIR

        photos = []
        stories = []

        with open(json_file, 'rb') as fl:
            data = json.load(fl)

            for feature in data['features']:
                if feature['properties']['story_type'] == 'photo':
                    photos.append(feature['properties'])
                else:
                    stories.append(feature['properties'])

        return photos, stories

    def render_development_html(self, target):
        env = Environment(loader=FileSystemLoader(
            '%s/demolitions/templates' % PROJECT_DIR))
        template = env.get_template(target + '.html')

        photos, stories = self.read_json()

        output = template.render(
            photos=photos,
            stories=stories,
            demolitions_css=DEMOLITIONS_CSS,
            demolitions_js=DEMOLITIONS_JS,
            event_tracking_js=EVENT_TRACKING_JS
        ).encode('utf8')

        file_path = "%s/demolitions/" % PROJECT_DIR + \
            "static/%s.html" % target

        with open(file_path, "wb") as index_file:
            index_file.write(output)

    def render_production_html(self, target):
        env = Environment(loader=FileSystemLoader(
            '%s/demolitions/templates' % PROJECT_DIR))
        template = env.get_template(target + '.html')

        photos, stories = self.read_json()

        output = template.render(
            photos=photos,
            stories=stories,
            demolitions_css=RENDER_DEMOLITIONS_CSS,
            demolitions_js=RENDER_DEMOLITIONS_JS,
            event_tracking_js=RENDER_EVENT_TRACKING_JS
        ).encode('utf8')

        file_path = "%s/demolitions/" % PROJECT_DIR + \
            "static/html/%s.html" % target

        with open(file_path, "wb") as index_file:
            index_file.write(output)

if __name__ == '__main__':
    Render()
