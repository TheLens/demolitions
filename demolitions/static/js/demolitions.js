(function () {
  'use strict';
  /*global $, L, PhotoSwipe, PhotoSwipeUI_Default */
  /*jslint browser: true*/

  var map,
    data,
    parishOutlineData,
    introTilesLayer,
    mainTilesLayer,
    markersLayer,
    introLegend,
    mainLegend,
    window_resize_timeout;

  var ne = [30.071173775590747, -89.87503051757812];
  var sw = [29.91387643831764, -90.13870239257812];

  function isSmall() {
    var width = window.innerWidth;

    if (width <= 600) {
      return true;
    }

    return false;
  }

  function isMobile() {
    var width = window.innerWidth;

    if (width <= 640) {
      return true;
    }

    return false;
  }

  function isMedium() {
    var width = window.innerWidth;

    if (width > 600 && width <= 1200) {
      return true;
    }

    return false;
  }

  function isLarge() {
    var width = window.innerWidth;

    if (width > 1000) {
      return true;
    }

    return false;
  }

  function isRetinaDisplay() {
    if (window.matchMedia) {
      var mq = window.matchMedia("only screen and (min--moz-device-pixel-ratio: 1.3), only screen and (-o-min-device-pixel-ratio: 2.6/2), only screen and (-webkit-min-device-pixel-ratio: 1.3), only screen  and (min-device-pixel-ratio: 1.3), only screen and (min-resolution: 1.3dppx)");
      return ((mq && mq.matches) || (window.devicePixelRatio > 1));
    }
  }

  function openPhotoSwipe(slug, target) {
    var i, j, dict, dimensions, file_size;
    var items = [];
    var photos = [];
    var S3_url = 'https://s3-us-west-2.amazonaws.com/projects.thelensnola.org/demolitions/images';
    var features = data.features;
    var pswpElement = document.querySelectorAll('.pswp')[0];

    for (i = 0; i < features.length; i++) {
      if (features[i].properties.slug === slug) {
        photos = features[i].properties.photos;
      }
    }

    for (j = 0; j < photos.length; j++) {
      dict = {};

      dict.title = '<p class="gallery-cutline">' + photos[j].date + ' <span class="gallery-source right">' +
        photos[j].source + '</span><p class="gallery-cutline">' + photos[j].caption + '</p>';

      // Determine file size needed.
      if (isRetinaDisplay()) {
        if (isSmall()) {
          file_size = photos[j].filename.medium;// 1200px wide/high
        } else if (isMedium()) {
          file_size = photos[j].filename.large;// 2400px wide/high
        } else {
          file_size = photos[j].filename.xlarge;// 4000px wide/high
        }
      } else {
        if (isSmall()) {
          file_size = photos[j].filename.small;// 600px wide
        } else if (isMedium()) {
          file_size = photos[j].filename.medium;// 1200px wide/high
        } else {
          file_size = photos[j].filename.large;// 2400px wide/high
        }
      }

      dict.src = S3_url + '/' + slug + '/' + file_size;
      dict.msrc = S3_url + '/' + slug + '/' + photos[j].filename.small;

      dimensions = file_size.match(/(\d+)x(\d+)/g)[0];
      dict.w = parseInt(dimensions.split('x')[0], 10);
      dict.h = parseInt(dimensions.split('x')[1], 10);

      items.push(dict);
    }

    var options = {
      history: false,
      focus: false,
      showAnimationDuration: 0,
      hideAnimationDuration: 0
    };

    var gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, items, options);
    gallery.init();

    // Go to the photo that was clicked.
    var clicked_index = parseInt(target.dataset.photoIndex, 10) - 1;
    gallery.goTo(clicked_index);

    changeWidthBasedElements(); // To abbreviate sources
  }

  function initiateMap() {
    map = new L.Map("map", {
      minZoom: 10,
      maxZoom: 18,
      scrollWheelZoom: true,
      fadeAnimation: false,
      zoomControl: false
    }).fitBounds(
      [ne, sw],
      {padding: [0, 0]}
    );
  }

  function addZoomIcons() {
    L.control.zoom({position: 'topright'}).addTo(map);
  }

  function createIntroLegend() {
    introLegend = L.control({position: 'bottomleft'});

    introLegend.onAdd = function () {
      var div = L.DomUtil.create('div', 'legend intro-legend');
      div.innerHTML = '<i class="intro-marker-color"></i> Demolition permits';

      return div;
    };
  }

  function addIntroLegend() {
    introLegend.addTo(map);
  }

  function createMainLegend() {
    mainLegend = L.control({position: 'bottomleft'});

    mainLegend.onAdd = function () {
      var div = L.DomUtil.create('div', 'legend main-legend');
      div.innerHTML = '<i style="background-color: blue;"></i> Photos<br>' +
        '<i style="background-color: orange;"></i> Stories';

      return div;
    };
  }

  function addMainLegend() {
    mainLegend.addTo(map);
  }

  function openPopup(layer) {
    layer.openPopup(layer.getLatLng());
  }

  function clickFeature(e) {
    var layer = e.target;
    var slug = layer.feature.properties.slug;

    // debugger;

    updateSidebar(slug);
    openPopup(layer);
  }

  function setMarkerToActiveStyle(layer) {
    layer.setStyle({
      opacity: 1.0,
      fillOpacity: 1.0
    });
  }

  function setMarkerToHoverStyle(layer) {
    layer.setStyle({
      opacity: 0.9,
      fillOpacity: 0.9
    });
  }

  function setMarkerToInactiveStyle(layer) {
    layer.setStyle({
      opacity: 0.7,
      fillOpacity: 0.6
    });
  }

  function highlightFeature(e) {
    var layer = e.target;
    if (layer.options.opacity !== 1.0) {// If not active
      setMarkerToHoverStyle(layer);
    }
  }

  function resetHighlight(e) {
    var layer = e.target;
    if (layer.options.opacity === 0.9) {// If hover
      setMarkerToInactiveStyle(layer);
    }
  }

  function onEachFeature(feature, layer) {
    layer.on({
      click: clickFeature,
      mouseover: highlightFeature,
      mouseout: resetHighlight
    });
  }

  function createIntroTiles() {
    var multiplier = '';
    var access_token = 'pk.eyJ1IjoidHRob3JlbiIsImEiOiJEbnRCdmlrIn0.hX5nW5GQ-J4ayOS-3UQl5w';

    if (isRetinaDisplay()) {
      multiplier = '';
    }

    var tile_url = 'https://api.mapbox.com/v4/tthoren.e1f67181/{z}/{x}/{y}' +
      multiplier + '.png?access_token=' + access_token;

    introTilesLayer = L.tileLayer(
      tile_url,
      {
        attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox. &copy; OpenStreetMap</a>.",
        detectRetina: true
      }
    );
  }

  function createMainTiles() {
    var multiplier = '';
    var access_token = 'pk.eyJ1IjoidHRob3JlbiIsImEiOiJEbnRCdmlrIn0.hX5nW5GQ-J4ayOS-3UQl5w';

    if (isRetinaDisplay()) {
      multiplier = '';
    }

    var tile_url = 'https://api.mapbox.com/v4/tthoren.49f1de96/{z}/{x}/{y}' +
      multiplier + '.png?access_token=' + access_token;

    mainTilesLayer = L.tileLayer(
      tile_url,
      {
        attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox. &copy; OpenStreetMap</a>.",
        detectRetina: true
      }
    );
  }

  function createMarkersLayer() {
    markersLayer = L.geoJson(data, {
      onEachFeature: onEachFeature,
      pointToLayer: function (feature, layer) {
        return L.circleMarker(layer, {
          radius: isMobile() ? 10 : 7,
          color: '#DDDDDD',
          opacity: 0.7,
          fillColor: feature.properties.story_type === 'story' ? 'orange' : 'blue',
          fillOpacity: 0.6,
          popupAnchor: [100, 100]
        }).bindPopup(
          '<span class="address-label">' + feature.properties.address + '</span>',
          {
            offset: isMobile() ? new L.point(0, -11) : new L.point(0, -8),
            autoPan: true
          }
        );
      },
    });
  }

  function createParishLayer() {
    var parishTopoLayer = topojson.feature(parishOutlineData, parishOutlineData.objects['orleans-no-lake']);
    var parishLayer = L.geoJson(parishTopoLayer, {
      filter: function (feature, layer) {
        if (feature.properties) {
          // If the property "underConstruction" exists and is true, return false (don't render features under construction)
          return feature.properties.underConstruction !== undefined ? !feature.properties.underConstruction : true;
        }
        return false;
      },
      style: {
        fillOpacity: 0,
        color: "white",
        opacity: 1,
        weight: 1.0,
        dashArray: '5, 5',
        clickable: false
      }
    });

    parishLayer.addTo(map);
  }

  function getCurrentSlug() {
    var slug = window.location.hash.split('#')[1];

    if (typeof slug === 'undefined') {
      slug = 'home';
    }

    return slug;
  }

  function updateSidebar(new_slug, prev_slug) {
    var previous_slug;

    if (prev_slug !== undefined) {
      previous_slug = prev_slug;
    } else {
      previous_slug = getCurrentSlug();
    }

    if (new_slug === previous_slug) {
      return;
    }

    window.location.hash = '#' + new_slug;

    document.getElementById(previous_slug).style.display = 'none';
    document.getElementById(new_slug).style.display = 'block';

    // Scroll to top
    $('#' + new_slug).scrollTop(0);
    document.body.scrollTop = document.documentElement.scrollTop = 0;

    updateImagesSrc(new_slug);

    if (new_slug === 'home' || new_slug === 'about') {
      showIntroMap();
      showIntroStyles();
    } else {
      showDotMap(previous_slug);
      showMainStyles();
    }
  }

  function syncMapWithSidebar(slug, must_zoom, previous_slug) {
    // Find the marker with this slug.
    markersLayer.eachLayer(function (layer) {
      // Open popup and modify styles
      if (layer.feature.properties.slug === slug) {
        // Change map center and zoom
        var lat = layer._latlng.lat;
        var lon = layer._latlng.lng;

        var current_slug = getCurrentSlug();

        var mapBounds = map.getBounds();//_northEast, _southWest (lat, lng)
        var bbTopRight = mapBounds._northEast;
        var bbBottomLeft = mapBounds._southWest;

        var isInBounds = (bbTopRight.lat >= lat && bbBottomLeft.lat <= lat && bbTopRight.lng >= lon && bbBottomLeft.lng <= lon);

        // debugger;

        if (must_zoom === true) {// Always zoom in on phone
          map.setView(
            {lon: lon, lat: lat},
            15
          );
        } else if (previous_slug === 'home') {// Launch
          map.fitBounds(
            [ne, sw],
            {padding: [0, 0]}
          );
        } else if (!layer._popup._isOpen) {// Default is to zoom in. Don't change if clicked
          map.setView(
            {lon: lon, lat: lat},
            15
          );
        }

        openPopup(layer);
        setMarkerToActiveStyle(layer);
      } else {
        setMarkerToInactiveStyle(layer);
      }
    });
  }

  function selectDropdownListener() {
    $('#select').on('change', function (e) {
      var new_id = e.target.value;
      updateSidebar(new_id);
    });
  }

  function calculateNewSidebarId(direction) {
    var i, new_index, new_slug;
    var previous_slug = getCurrentSlug();

    // Find ID in marker data JSON
    for (i = 0; i < data.features.length; i++) {
      if (data.features[i].properties.slug === previous_slug) {
        new_index = i + direction;
      }
    }

    // Check if fall off end of story IDs.
    if (new_index < 0) {
      new_slug = data.features[data.features.length - 1].properties.slug;
    } else if (new_index > (data.features.length - 1)) {
      new_slug = data.features[0].properties.slug;
    } else {
      new_slug = data.features[new_index].properties.slug;
    }

    return new_slug;
  }

  function navigateSidebarListener() {
    var new_slug;

    $('#previous-button').on('click', function () {
      document.getElementById('select').value = "";  // Revert select menu
      new_slug = calculateNewSidebarId(-1);
      updateSidebar(new_slug);
    });

    $(document).keydown(function(e){
      var key = e.which;
      if (key === 37) {// Key left.
        document.getElementById('select').value = "";  // Revert select menu
        new_slug = calculateNewSidebarId(-1);
        updateSidebar(new_slug);
      }
      if (key === 39) {// Key right.
        document.getElementById('select').value = "";  // Revert select menu
        new_slug = calculateNewSidebarId(1);
        updateSidebar(new_slug);
      }
    });

    $('#next-button').on('click', function () {
      document.getElementById('select').value = "";  // Revert select menu
      new_slug = calculateNewSidebarId(1);
      updateSidebar(new_slug);
    });
  }

  function updateImagesSrc(id) {
    /* Add or update src URLs for all images in this story/photo */

    // Get list of all img tags
    var i, img, src;
    var images = document.getElementById(id).getElementsByTagName("img");

    // Loop through images and change src attributes
    for (i = 0; i < images.length; i++) {
      img = images[i];
      src = img.dataset.src;

      img.src = src;
    }
  }

  function clickPhotoGalleryListener() {
    $('.photo-gallery').on('click', function (e) {
      var slug = getCurrentSlug();
      openPhotoSwipe(slug, e.target);
    });
  }

  function clickLaunchButtonListener() {
    $('.launch-button').on('click', function () {
      $('.nav').css({'display': 'block'});
      var slug = '2316-new-orleans-st';
      updateSidebar(slug);
    });
  }

  function clickHomeButtonListener() {
    $('.go-home').on('click', function () {
      $('.about-nav').css({'display': 'none'});
      $('.nav').css({'display': 'none'});

      document.getElementById('map').style.display = 'block';

      updateSidebar('home');
    });
  }

  function clickAbout() {
    $('.about-link').on('click', function () {
      $('.about-nav').css({'display': 'block'});
      $('.nav').css({'display': 'none'});

      if (isMobile()) {
        document.getElementById('map').style.display = 'none';
      }

      updateSidebar('about');
    });
  }

  function abbreviatePhotoSource() {
    var long_string = 'The Historic New Orleans Collection, gift of FEMA';
    var short_string = 'HNOC, gift of FEMA';

    var i, j, contents;
    var current_slug = getCurrentSlug();
    var current_story = document.getElementById(current_slug);
    var credits = current_story.getElementsByClassName('source');

    for (i = 0; i < credits.length; i++) {
      contents = credits[i].innerHTML;
      if (contents.indexOf(long_string) > -1) {
        credits[i].innerHTML = short_string;
      }
    }

    var slideshow_credits = document.getElementsByClassName('gallery-source');

    for (j = 0; j < slideshow_credits.length; j++) {
      contents = slideshow_credits[j].innerHTML;
      if (contents.indexOf(long_string) > -1) {
        slideshow_credits[j].innerHTML = short_string;
      }
    }
  }

  function elaboratePhotoSource() {
    var long_string = 'The Historic New Orleans Collection, gift of FEMA';
    var short_string = 'HNOC, gift of FEMA';

    var i, j, contents;
    var current_slug = getCurrentSlug();
    var current_story = document.getElementById(current_slug);
    var credits = current_story.getElementsByClassName('source');

    for (i = 0; i < credits.length; i++) {
      contents = credits[i].innerHTML;
      if (contents.indexOf(short_string) > -1) {
        credits[i].innerHTML = long_string;
      }
    }

    var slideshow_credits = document.getElementsByClassName('gallery-source');

    for (j = 0; j < slideshow_credits.length; j++) {
      contents = slideshow_credits[j].innerHTML;
      if (contents.indexOf(short_string) > -1) {
        slideshow_credits[j].innerHTML = long_string;
      }
    }
  }

  function changeWidthBasedElements() {
    var header_img;
    var current_slug = getCurrentSlug();
    var screenWidth = document.documentElement.clientWidth;

    // Headlines
    if (screenWidth <= 640) {
      // Turn off map.scrollWheelZoom
      map.scrollWheelZoom.disable();

      // Abbreviate credit for HNOC
      abbreviatePhotoSource();
    } else {
      document.getElementById('map').style.display = 'block';

      // Turn on map.scrollWheelZoom
      map.scrollWheelZoom.enable();

      // Revert
      elaboratePhotoSource();
    }
  }

  function windowResizeListener() {
    window.addEventListener('resize', function(e) {
      clearTimeout(window_resize_timeout);
      window_resize_timeout = setTimeout(changeWidthBasedElements, 100);
    });
    changeWidthBasedElements();
  }

  function hashChangeListener() {
    var previous_slug = getCurrentSlug();
    var current_slug = getCurrentSlug();

    window.onhashchange = function() {
      previous_slug = current_slug;
      current_slug = getCurrentSlug();

      updateSidebar(current_slug, previous_slug);
    };
  }

  function setEventListeners() {
    selectDropdownListener();
    navigateSidebarListener();
    clickPhotoGalleryListener();
    clickLaunchButtonListener();
    clickHomeButtonListener();
    clickAbout();
    windowResizeListener();
    hashChangeListener();
  }

  function showIntroMap() {
    if (map.hasLayer(markersLayer)) {
      map.removeLayer(markersLayer);
    }

    if (map.hasLayer(mainTilesLayer)) {
      map.removeLayer(mainTilesLayer);
    }

    if (!introTilesLayer) {  // Check if introTilesLayer has been initiated
      createIntroTiles();
    }

    map.addLayer(introTilesLayer);

    map.options.maxZoom = 14;

    map.fitBounds(  // Fit map to New Orleans
      [ne, sw],
      {
        padding: [0, 0]
      }
    );

    if (!introLegend) {  // Check if introLegend has been initiated
      createIntroLegend();
      addIntroLegend();
    }

    // Map legends
    $('.intro-legend').css({'display': 'block'});
    $('.main-legend').css({'display': 'none'});
  }

  function showDotMap(previous_slug) {
    if (map.hasLayer(introTilesLayer)) {
      map.removeLayer(introTilesLayer);
    }

    if (!mainTilesLayer) {
      createMainTiles();
    }

    map.addLayer(mainTilesLayer);

    if (!markersLayer) {  // Check if markersLayer has been initiated
      createMarkersLayer();
    }

    map.addLayer(markersLayer);

    map.options.maxZoom = 18;

    var slug = getCurrentSlug();

    // Don't want to trigger zoom on switch between intro/heatmap and markers
    var mustZoom = isMobile();
    syncMapWithSidebar(slug, mustZoom, previous_slug);

    if (!mainLegend) {  // Check if mainLegend has been initiated
      createMainLegend();
      addMainLegend();
    }

    // Map legends
    $('.intro-legend').css({'display': 'none'});
    $('.main-legend').css({'display': 'block'});
  }

  function displaySidebar(slug) {
    document.getElementById(slug).style.display = 'block';
    updateImagesSrc(slug);
  }

  function showIntroStyles() {
    var slug = getCurrentSlug();

    $('.nav').css({'display': 'none'});

    if (slug === 'about' && isMobile()) {
      document.getElementById('map').style.display = 'none';
    }
  }

  function showMainStyles() {
    $('.nav').css({'display': 'block'});
    $('.about-nav').css({'display': 'none'});
  }

  function startAppWithIntroView() {
    // Async load dot data
    $.getJSON('https://s3-us-west-2.amazonaws.com/projects.thelensnola.org/demolitions/data/reduced.json', function (info) {
      data = info;  // data is a global variable
      createMarkersLayer();  // Lazy load markers
    });

    $.getJSON('https://s3-us-west-2.amazonaws.com/projects.thelensnola.org/demolitions/data/orleans-topo.json', function (info) {
      parishOutlineData = info;
      createParishLayer();
    });

    // Hide this layer under the intro layer to avoid loading during switch.
    createMainTiles();
    map.addLayer(mainTilesLayer);

    showIntroMap();
    showIntroStyles();
  }

  function startAppWithMainView() {
    $.getJSON('https://s3-us-west-2.amazonaws.com/projects.thelensnola.org/demolitions/data/reduced.json', function (info) {
      data = info;
      showDotMap();
      showMainStyles();
    });

    $.getJSON('https://s3-us-west-2.amazonaws.com/projects.thelensnola.org/demolitions/data/orleans-topo.json', function (info) {
      parishOutlineData = info;
      createParishLayer();
    });

    createIntroTiles();
  }

  function enterApp() {
    var slug = getCurrentSlug();

    initiateMap();
    addZoomIcons();

    if (slug === 'home') {
      startAppWithIntroView();
    } else if (slug === 'about') {
      startAppWithIntroView();
    } else {
      startAppWithMainView();
    }

    displaySidebar(slug);
  }

  $(document).ready(function () {
    enterApp();
    setEventListeners();
  });

}());