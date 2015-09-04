
'''
Accesses various other scripts to piece together data and form a single
JSON file that is then used to render the app and provide data for the front
end.
'''

import fabfile
from scripts.photos import Photo
from scripts.docs import Doc
from scripts.combine import Combine
from scripts.render import Render
from scripts import google_photos_id, google_doc_ids


if __name__ == '__main__':
    # 1. Download Google Sheet, parse CSV and export to JSON.
    Photo(sheet_id=google_photos_id)

    # 2. Download Google Docs, parse contents and export to JSON.
    Doc(google_doc_ids)

    # 3. Geocode, clean, combine photo and story JSON files into single JSON.
    Combine()

    # 4. Render HTML from JSON.
    Render()

    # 5. Upload files to S3.
    fabfile.s3()
