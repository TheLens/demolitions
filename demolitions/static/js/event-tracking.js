/* global ga */

var bannerLensLogo = document.getElementById('lens-logo');
var bannerNationLogo = document.getElementById('nation-logo');
var bannerTitle = document.getElementById('banner-title');
var bannerFacebookIcon = document.getElementById('banner-facebook');
var bannerTwitterIcon = document.getElementById('banner-twitter');

// Banner Lens logo
addListener(bannerLensLogo, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Banner Lens logo');
});

// Banner Nation logo
addListener(bannerNationLogo, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Banner Nation logo');
});

// Banner title
addListener(bannerTitle, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Banner title');
});

// Banner Facebook icon
addListener(bannerFacebookIcon, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Banner Facebook icon');
});

// Banner Twitter icon
addListener(bannerTwitterIcon, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Banner Twitter icon');
});


var navPrevious = document.getElementById('previous-button');
var navNext = document.getElementById('next-button');
var navSelect = document.getElementById('select');

// Nav bar previous button
addListener(navPrevious, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Nav previous button');
});

// Nav bar next button
addListener(navNext, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Nav next button');
});

// Nav bar select menu
addListener(navSelect, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Nav select menu');
});

var photoGallery = $('.photo-gallery');
photoGallery.on('click', function () {
  ga('send', 'event', 'link', 'click', 'Open photo gallery');
});


var launchButton = document.getElementById('launch-button');
addListener(launchButton, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Click "Explore" button');
});

var aboutLink = document.getElementById('about-link');
addListener(aboutLink, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Click "About this project" link');
});

// Donate buttons
var lensDonateButton = document.getElementById('lens-donate');
var nationDonateButton = document.getElementById('nation-donate');

addListener(lensDonateButton, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Click Lens donate button');
});
addListener(nationDonateButton, 'click', function () {
  ga('send', 'event', 'link', 'click', 'Click Nation donate button');
});


/**
 * Utility to wrap the different behaviors between W3C-compliant browsers
 * and IE when adding event handlers.
 *
 * @param {Object} element Object on which to attach the event listener.
 * @param {string} type A string representing the event type to listen for
 *     (e.g. load, click, etc.).
 * @param {function()} callback The function that receives the notification.
 */
function addListener(element, type, callback) {
  if (element.addEventListener) {
    element.addEventListener(type, callback);
  } else if (element.attachEvent) {
    element.attachEvent('on' + type, callback);
  }
}
