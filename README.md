# Nitroradical

Scrape the [BBC iPlayer](http://www.bbc.co.uk/iplayer/) TV listings
by category and displays the programme info for that category as JSON.

Proof of concept for now.

## Why?

Because the BBC recently stopped their RSS feeds for iPlayer. They have
a replacement API (Nitro), but that's only open to BBC employees right
now :(

## Install

Install dependencies using `pip install -r requirements.txt`.

## Usage

`nitroradical.py <category name>`

e.g. `nitroradical.py films`

## Not implemented yet

* Getting [BBC Programme Identifiers](https://en.wikipedia.org/wiki/BBC_Programme_Identifier)
for shows with multiple episodes.
* Extracting information from flags (e.g. HD, audio described).
* Outputting this information as RSS (if there's interest).
* Tests!
