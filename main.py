#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
from __future__ import print_function

import codecs
import sys


def main():
    pass


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    main()
