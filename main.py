#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
from __future__ import print_function

import codecs
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
    next_disabled = etree.xpath('//span[@class="next disabled txt"]')
    if next_disabled:
        return True
    else:
        return False


def iterate_through_index(category):
    # download page
    # process content = get_items_from_page (TODO: episodes)
    # create RSS items
    # download first page
    last_page = False
    page_number = 0
    while not last_page:
        page_number += 1
        url = ("http://www.bbc.co.uk/iplayer/categories/{}"
               "/all?sort=atoz&page={}".format(category, page_number))
        logging.info("Downloading page {}".format(page_number))
        etree = get_page_as_element_tree(url)
        last_page = is_last_page(etree)

def main():
    logging.basicConfig(level=logging.INFO)
    dshelpers.install_cache(10000000000)
    iterate_through_index('documentaries')

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    main()
