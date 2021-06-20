#!/usr/bin/env python
# encoding: utf-8

# Copyright 2014 Steven Maude

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import datetime
import json
import logging
import sys

import dshelpers
import lxml.html
import PyRSS2Gen


def get_page_as_element_tree(url):
    """ Take URL as string; return lxml etree of HTML. """
    html = dshelpers.request_url(url).text
    return lxml.html.fromstring(html)


def is_last_page(etree):
    """ Return True if current page is final index page, otherwise False. """
    next_disabled = etree.xpath(
        '//span[contains(@class, "lnk--disabled") and contains(@class, "pagination__direction--next")]'
    )
    return True if len(next_disabled) > 0 else False


def parse_items_from_page(etree):
    """ Parse programme data from index page; return list of dicts of data. """
    (page_data,) = etree.xpath(
        '//script[@id="tvip-script-app-store"]//text()', smart_strings=False
    )
    assert page_data.startswith("window.__IPLAYER_REDUX_STATE__ = ")

    page_data = page_data.lstrip("window.__IPLAYER_REDUX_STATE__ = ").rstrip(
        ";"
    )
    programme_json = json.loads(page_data)

    programmes = []
    for entity in programme_json["entities"]:
        programme = {}
        try:
            subtitle = entity["props"]["subtitle"]
        except KeyError:
            subtitle = ""
        programme["title"] = " — ".join([entity["props"]["title"], subtitle])
        programme["synopsis"] = entity["props"]["synopsis"]
        programme["url"] = "".join(
            ["https://www.bbc.co.uk", entity["props"]["href"]]
        )
        programmes.append(programme)

    return programmes


def iterate_through_index(category):
    """ Iterate over index pages; return list of programme data dicts. """
    last_page = False
    page_number = 0
    items = []

    while not last_page:
        page_number += 1
        url = (
            "https://www.bbc.co.uk/iplayer/categories/{}"
            "/most-recent?page={}".format(category, page_number)
        )
        logging.info("Downloading page {}".format(page_number))
        etree = get_page_as_element_tree(url)
        items.extend(parse_items_from_page(etree))
        last_page = is_last_page(etree)

    return items


def convert_items_to_rss(items):
    """ Take list of dicts of programmes; return list of RSSItems. """
    return [
        PyRSS2Gen.RSSItem(
            title=item["title"], link=item["url"], description=item["synopsis"]
        )
        for item in items
    ]


def write_rss_feed(category, items):
    """ Write RSS feed of programmes. """
    rss_items = convert_items_to_rss(items)
    rss = PyRSS2Gen.RSS2(
        title="BBC iPlayer feed for {}".format(category),
        link="https://www.bbc.co.uk/iplayer",
        description="BBC iPlayer: {}".format(category),
        lastBuildDate=datetime.datetime.now(),
        items=rss_items,
    )
    with open("iPlayer_{}.xml".format(category), "w") as f:
        rss.write_xml(f, "utf-8")


def main():
    """ Scrape BBC iPlayer web frontend category; create JSON feed. """
    logging.basicConfig(level=logging.INFO)
    dshelpers.install_cache(expire_after=30 * 60)

    allowed_categories = [
        "arts",
        "cbbc",
        "cbeebies",
        "comedy",
        "documentaries",
        "drama-and-soaps",
        "entertainment",
        "films",
        "food",
        "history",
        "lifestyle",
        "music",
        "news",
        "science-and-nature",
        "sport",
        "audio-described",
        "signed",
        "northern-ireland",
        "scotland",
        "wales",
    ]

    if len(sys.argv) == 2 and sys.argv[1] in allowed_categories:
        category = sys.argv[1]
        items = iterate_through_index(category)
        print(json.dumps(items, indent=4))
        write_rss_feed(category, items)
    else:
        print("Usage: nitroradical.py <category name>")
        print("Allowed categories:")
        print(", ".join(allowed_categories))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
