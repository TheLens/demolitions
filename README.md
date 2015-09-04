## Missing Home: Demolitions in post-Katrina New Orleans

This is the code that gathers, builds, renders and displays the page at http://projects.thelensnola.org/demolitions/. Much of the code is very specific to The Lens and this project, unfortunately, but you are welcome to take any of the code and modify it to your needs.

### How it works

The project is powered by a "backend" of Google Docs and Sheets. All stories were written in Google Docs and formatted in the [ArchieML](http://archieml.org/) markup language. Photo data was organized using Google Sheets.

The raw images are processed and scaled using ImageMagick.

The data from the stories and the spreadsheet is combined into a single JSON object that represents each of the ~150 locations in the project. That data is used to render the front-end HTML, and a selection of the JSON is then sent to power the front-end's map and navigation. There are two versions of the rendered HTML: one for The Lens, and another that was used in an iframe on [The Nation's website](http://www.thenation.com/article/missing-home-the-demolition-of-new-orleans-after-katrina/).

Finally, all photos and front-end code is uploaded to Amazon S3, where it serves the page.

#### Libraries used

* [ArchieML](http://archieml.org/)/[ArchieML-python](https://github.com/brainkim/archieml-python)
* [ImageMagick](http://www.imagemagick.org/script/index.php)
* [PhotoSwipe](http://photoswipe.com/)
* [pym.js](http://blog.apps.npr.org/pym.js/)
* [TopoJSON](https://github.com/mbostock/topojson)