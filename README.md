# Nitroradical

Scrape the [BBC iPlayer](http://www.bbc.co.uk/iplayer/) TV listings
by category. It displays the programme info for that category as JSON
and outputs an RSS feed.

## Why?

Because the BBC recently stopped their RSS feeds for iPlayer. They have
a replacement API (Nitro), but that's only open to BBC employees right
now :(

## Install

Install dependencies using `pip install -r requirements.txt`.

Requires Python 3.7 or greater.

## Usage

`nitroradical.py <category name>`

e.g. `nitroradical.py films`

## Not implemented yet

* Handling multiple programme episodes. For programmes with multiple
  episodes, only the programme shown in the category listing is
  included.
* Getting detailed programme information.
* Radio information.
* Tests!
