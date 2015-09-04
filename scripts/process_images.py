
import os
from subprocess import call
from scripts import PROJECT_DIR


SELECTED_DIR = '%s/data/selected-photos' % PROJECT_DIR
OUTPUT_DIR = '%s/demolitions/static/images' % PROJECT_DIR


def process_images():
    print '\nProcessing images...'

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for subdir, dirs, files in os.walk(SELECTED_DIR):
        if subdir == SELECTED_DIR:
            continue

        file_excludes = [
            '.DS_Store',
            'Thumbs.db'
        ]

        for i, fl in enumerate(files):
            if fl in file_excludes:
                continue

            input_dir = subdir

            slug = input_dir.split('/')[-1]

            basename = os.path.basename(fl)  # name.jpg
            basename = os.path.splitext(basename)[0]  # name

            output_dir = "{0}/{1}".format(OUTPUT_DIR, slug)

            print output_dir

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # If FEMA/HNOC photo, crop out FEMA credit whitespace at bottom.
            if 'fema' in fl:
                fl_old = fl
                fl = fl.replace('-fema', '')

                call([
                    'convert',
                    '%s/%s' % (input_dir, fl_old),
                    '-gravity',
                    'south',
                    '-chop',
                    '0x100',
                    '%s/%s' % (input_dir, fl)
                ])

            # Regex out '-fema' in filename
            basename = basename.replace('-fema', '')

            # Small width
            call([
                'convert',
                '%s/%s' % (input_dir, fl),
                '-interlace',
                'plane',
                '-quality',
                '92',
                '-density',
                '72',
                '-resize',
                '600>',
                '-set',
                'filename:mysize',
                "%wx%h",
                "{0}/{1}-%[filename:mysize].jpg".format(output_dir, basename)
            ])

            # Medium width
            call([
                'convert',
                '%s/%s' % (input_dir, fl),
                '-interlace',
                'plane',
                '-quality',
                '92',
                '-density',
                '72',
                '-resize',
                '1200x1200>',  # Limit both width and height to 1200px
                '-set',
                'filename:mysize',
                "%wx%h",
                "{0}/{1}-%[filename:mysize].jpg".format(output_dir, basename)
            ])

            # Large width
            call([
                'convert',
                '%s/%s' % (input_dir, fl),
                '-interlace',
                'plane',
                '-quality',
                '92',
                '-density',
                '72',
                '-resize',
                '2400x2400>',  # Limit width to 2400px and height to 2000px
                '-set',
                'filename:mysize',
                "%wx%h",
                "{0}/{1}-%[filename:mysize].jpg".format(output_dir, basename)
            ])

            # Extra-large width
            call([
                'convert',
                '%s/%s' % (input_dir, fl),
                '-interlace',
                'plane',
                '-quality',
                '92',
                '-density',
                '72',
                '-resize',
                '4000x4000>',  # Limit width to 4000px and height to 2000px
                '-set',
                'filename:mysize',
                "%wx%h",
                "{0}/{1}-%[filename:mysize].jpg".format(output_dir, basename)
            ])

if __name__ == '__main__':
    process_images()
