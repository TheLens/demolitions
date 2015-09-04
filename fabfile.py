# -*- coding: utf-8 -*-

'''
Methods for deploying to S3.
'''

from fabric.api import local
from scripts import PROJECT_DIR


def minify():
    '''Minify static assets.'''

    minify_js()
    minify_css()


def minify_js():
    '''Minify JS files.'''

    js_dir = '%s/demolitions/static/js' % PROJECT_DIR

    local(
        'shopt -s nullglob\n' +
        'for f in %s/*.js; do\n' % js_dir +
        '  if [[ $f == *".min."* ]]; then\n' +
        '    continue\n' +
        '  fi\n' +
        '  filename="${f%.*}"\n' +
        '  yuicompressor $f -o $filename.min.js\n' +
        'done'
    )


def minify_css():
    '''Minify CSS files.'''

    css_dir = '%s/demolitions/static/css' % PROJECT_DIR
    skin_dir = '%s/demolitions/static/default-skin' % PROJECT_DIR

    local(
        'shopt -s nullglob\n' +
        'for f in %s/*.css; do\n' % css_dir +
        '  if [[ $f == *".min."* ]]; then\n' +
        '    continue\n' +
        '  fi\n' +
        '  filename="${f%.*}"\n' +
        '  yuicompressor $f -o $filename.min.css\n' +
        'done'
    )

    local(
        'shopt -s nullglob\n' +
        'for f in %s/*.css; do\n' % skin_dir +
        '  if [[ $f == *".min."* ]]; then\n' +
        '    continue\n' +
        '  fi\n' +
        '  filename="${f%.*}"\n' +
        '  yuicompressor $f -o $filename.min.css\n' +
        'done'
    )


def gzip():
    '''gzip static assets.'''

    gzip_html()
    gzip_js()
    gzip_json()
    gzip_css()


def gzip_html():
    '''gzip HTML files.'''

    html_dir = '%s/demolitions/static/html' % PROJECT_DIR
    temp_dir = '%s/html_temp' % html_dir

    local('mkdir %s' % temp_dir)

    local(
        'shopt -s nullglob\n' +
        'for f in %s/*.html; do\n' % html_dir +
        '  filename=$(basename $f)\n' +
        '  gzip -9 < $f > $f.gz;\n' +
        '  mv $f.gz %s/$filename\n' % temp_dir +
        'done')


def gzip_js():
    '''gzip JavaScript files.'''

    js_dir = '%s/demolitions/static/js' % PROJECT_DIR
    temp_dir = '%s/js_temp' % js_dir

    local('mkdir %s' % temp_dir)

    local(
        'shopt -s nullglob\n' +
        'for f in %s/*.min.js; do\n' % js_dir +
        '  filename=$(basename $f)\n' +
        '  gzip -9 < $f > $f.gz;\n' +
        '  mv $f.gz %s/$filename\n' % temp_dir +
        'done')


def gzip_json():
    # JSON
    app_data_dir = '%s/data/app' % PROJECT_DIR
    temp_dir = '%s/json_temp' % app_data_dir

    local('mkdir %s' % temp_dir)

    local(
        'shopt -s nullglob\n' +
        'for f in %s/*.json; do\n' % app_data_dir +
        '  filename=$(basename $f)\n' +
        '  gzip -9 < $f > $f.gz;\n' +
        '  mv $f.gz %s/$filename\n' % temp_dir +
        'done')


def gzip_css():
    '''gzip CSS files.'''

    css_dir = '%s/demolitions/static/css' % PROJECT_DIR
    skin_dir = '%s/demolitions/static/default-skin' % PROJECT_DIR

    temp_css_dir = '%s/css_temp' % css_dir
    temp_skin_dir = '%s/skin_temp' % skin_dir

    local('mkdir %s' % temp_css_dir)
    local('mkdir %s' % temp_skin_dir)

    local(
        'shopt -s nullglob\n' +
        'for f in %s/*.min.css; do\n' % css_dir +
        '  filename=$(basename $f)\n' +
        '  gzip -9 < $f > $f.gz;\n' +
        '  mv $f.gz %s/$filename\n' % temp_css_dir +
        'done')
    local(
        'shopt -s nullglob\n' +
        'for f in %s/*.min.css; do\n' % skin_dir +
        '  filename=$(basename $f)\n' +
        '  gzip -9 < $f > $f.gz;\n' +
        '  mv $f.gz %s/$filename\n' % temp_skin_dir +
        'done')


def clean_gzip():
    html_dir = '%s/demolitions/static/html' % PROJECT_DIR
    css_dir = '%s/demolitions/static/css' % PROJECT_DIR
    skin_dir = '%s/demolitions/static/default-skin' % PROJECT_DIR
    js_dir = '%s/demolitions/static/js' % PROJECT_DIR
    app_data_dir = '%s/data/app' % PROJECT_DIR

    local('rm -rf %s/html_temp' % html_dir)
    local('rm -rf %s/js_temp' % js_dir)
    local('rm -rf %s/json_temp' % app_data_dir)
    local('rm -rf %s/css_temp' % css_dir)
    local('rm -rf %s/skin_temp' % skin_dir)


def s3_images():
    '''Images only.'''

    local(
        'aws s3 sync %s/demolitions/static/images/ ' % PROJECT_DIR +
        's3://projects.thelensnola.org/demolitions/images/ ' +
        '--acl "public-read" '
        '--cache-control "max-age=86400"')


def s3_static():
    '''Static dir.'''

    js_dir = '%s/demolitions/static/js' % PROJECT_DIR
    css_dir = '%s/demolitions/static/css' % PROJECT_DIR
    skin_dir = '%s/demolitions/static/default-skin' % PROJECT_DIR
    app_data_dir = '%s/data/app' % PROJECT_DIR

    # HTML
    local(
        'aws s3 sync %s/demolitions/static/html/html_temp/ ' % PROJECT_DIR +
        's3://projects.thelensnola.org/demolitions/ ' +
        '--acl "public-read" ' +
        '--exclude=".DS_Store" ' +
        '--content-encoding gzip ' +
        '--content-type "text/html; charset=UTF-8" ' +
        '--cache-control "max-age=86400"')

    # JS
    local(
        'aws s3 sync %s/js_temp/ ' % js_dir +
        's3://projects.thelensnola.org/demolitions/js/ ' +
        '--acl "public-read" ' +
        '--exclude=".DS_Store" ' +
        '--content-encoding gzip ' +
        '--cache-control "max-age=86400"')

    # CSS
    local(
        'aws s3 sync %s/css_temp/ ' % css_dir +
        's3://projects.thelensnola.org/demolitions/css/ ' +
        '--acl "public-read" ' +
        '--exclude=".DS_Store" ' +
        '--content-encoding gzip ' +
        '--cache-control "max-age=86400"')

    # PhotoSwipe
    local(
        'aws s3 sync %s/ ' % skin_dir +
        's3://projects.thelensnola.org/demolitions/default-skin/ ' +
        '--acl "public-read" ' +
        '--exclude=".DS_Store" ' +
        '--cache-control "max-age=86400"')
    local(
        'aws s3 sync %s/skin_temp/ ' % skin_dir +
        's3://projects.thelensnola.org/demolitions/default-skin/ ' +
        '--acl "public-read" ' +
        '--exclude=".DS_Store" ' +
        '--content-encoding gzip ' +
        '--cache-control "max-age=86400"')

    # Data
    local(
        'aws s3 sync %s/json_temp/ ' % app_data_dir +
        's3://projects.thelensnola.org/demolitions/data/ ' +
        '--acl "public-read" ' +
        '--exclude=".DS_Store" ' +
        '--content-encoding gzip ' +
        '--cache-control "max-age=86400"')


def s3():
    '''Push everything to S3.'''

    clean_gzip()

    minify()
    gzip()

    s3_static()
    s3_images()

    clean_gzip()
