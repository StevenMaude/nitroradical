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
from __future__ import unicode_literals
from __future__ import print_function

import codecs
import datetime
import json
import logging
import sys

from collections import OrderedDict

import dshelpers
import lxml.html
import PyRSS2Gen


def get_page_as_element_tree(url):
    """ Take URL as string; return lxml etree of HTML. """
    html = dshelpers.request_url(url).text
    return lxml.html.fromstring(html)


def is_last_page(etree):
    """ Return True if current page is final index page, otherwise False. """
    next_disabled = etree.xpath('//span[@class="next disabled txt"]')
    next_present = etree.xpath('//span[@class="next txt"]')
    if next_disabled or not next_present:
        return True
    else:
        return False


def extract_programme_data(programme):
    """ Take programme etree; return dict containing programmed data. """
    # TODO: audio described, HD, signed flags
    programme_data = OrderedDict()
    programme_data['title'] = programme.xpath(
        './/div[@class="title top-title"]')[0].text.strip()
    try:
        programme_data['subtitle'] = programme.xpath(
            './/div[@class="subtitle"]')[0].text.strip()
    except IndexError:
        pass
    programme_data['synopsis'] = programme.xpath(
        './/p[@class="synopsis"]')[0].text.strip()
    programme_data['channel'] = programme.xpath(
        './/span[@class="small"]')[0].text.strip()
    try:
        programme_data['release'] = programme.xpath(
            './/span[@class="release"]')[0].text.strip()
    except IndexError:
        pass
    href, = programme.xpath('./a/@href')
    programme_data['url'] = ('http://www.bbc.co.uk' + href)
    programme_data['pid'] = href.split('/')[3]
    return programme_data


def parse_items_from_page(etree):
    """ Parse programme data from index page; return list of dicts of data. """
    programmes = etree.xpath('//li[@class="list-item programme"]')
    programmes_data = [extract_programme_data(programme)
                       for programme in programmes]
    return programmes_data


def iterate_through_index(category):
    """ Iterate over index pages; return list of programme data dicts. """
    last_page = False
    page_number = 0
    items = []

    while not last_page:
        page_number += 1
        url = ("http://www.bbc.co.uk/iplayer/categories/{}"
               "/all?sort=atoz&page={}".format(category, page_number))
        logging.info("Downloading page {}".format(page_number))
        etree = get_page_as_element_tree(url)
        parse_items_from_page(etree)
        items.extend(parse_items_from_page(etree))
        last_page = is_last_page(etree)

    return items


def convert_items_to_rss(items):
    """ Take list of dicts of programmes; return list of RSSItems. """
    return [PyRSS2Gen.RSSItem(
            title=item['title'],
            link=item['url'],
            description=item['synopsis']) for item in items]


def write_rss_feed(category, items):
    """ Write RSS feed of programmes. """
    rss_items = convert_items_to_rss(items)
    rss = PyRSS2Gen.RSS2(
        title="BBC iPlayer feed for {}".format(category),
        link="http://www.bbc.co.uk/iplayer",
        description="BBC iPlayer: {}".format(category),
        lastBuildDate=datetime.datetime.now(),
        items=rss_items)
    rss.write_xml(open("iPlayer_{}.xml".format(category), 'w'), 'utf-8')


def main():
    """ Scrape BBC iPlayer web frontend category; create JSON feed. """
    logging.basicConfig(level=logging.INFO)
    dshelpers.install_cache(expire_after=30*60)

    allowed_categories = ['arts', 'cbbc', 'cbeebies', 'comedy',
                          'documentaries', 'drama-and-soaps', 'entertainment',
                          'films', 'food', 'history', 'lifestyle', 'music',
                          'news', 'science-and-nature', 'sport',
                          'audio-described', 'signed', 'northern-ireland',
                          'scotland', 'wales']

    if len(sys.argv) == 2 and sys.argv[1] in allowed_categories:
        category = sys.argv[1]
        items = iterate_through_index(category)
        print(json.dumps(items, indent=4))
        write_rss_feed(category, items)
    else:
        print("Usage: nitroradical.py <category name>")
        print("Allowed categories:")
        print(', '.join(allowed_categories))

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    main()
