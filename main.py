#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
from __future__ import print_function

import codecs
import logging
import sys

from collections import OrderedDict

import dshelpers
import lxml.html


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
        items.append(parse_items_from_page(etree))
        last_page = is_last_page(etree)

    return items


def main():
    logging.basicConfig(level=logging.INFO)
    dshelpers.install_cache(10000000000)
    iterate_through_index('documentaries')

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    main()
