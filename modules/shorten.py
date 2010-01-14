#!/usr/bin/env python
#
# Copyright (C) 2007-2008 Christopher Jones
#
# This file is part of Madcow.
#
# Madcow is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Madcow is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with Madcow.  If not, see <http://www.gnu.org/licenses/>.

"""Shorten URLs with Metamark"""

from include.utils import Module
import logging as log
import re
import urllib
import BeautifulSoup

__version__ = '0.1'
__author__ = 'Will Nowak <wan@ccs.neu.edu>'
__all__ = []

class Shorten(Module):

    pattern = re.compile(r'(https?:\/\/[\w.]+\/?\S*)', re.I)
    require_addressing = False
    help = u'url shortener'

    def __init__(self, madcow=None):
        self.madcow = madcow
        self.max_length = 30

    def gethtmltitle(self, doc):
        try:
            data = doc.read()
            b = BeautifulSoup.BeautifulSoup(data)
            titlestr = b.find('title').string
            for x in ['\r', '\n', '\t']:
                titlestr = titlestr.replace(x, '')
            if len(titlestr) > self.max_length:
                return titlestr[:self.max_length] + '...'
            else:
                return titlestr
        except:
            return 'text/html'

    def gettitle(self, uri):
        try:
            f = urllib.urlopen(uri)
            content_type = f.info().gettype()
            if (content_type != 'text/html'):
                return '*content type* %s' % content_type
            else:
                return self.gethtmltitle(f)
        except:
            return False
 
    def tiny_url(self, url):
        """tinyurl"""
        try:
          if not len(url) > self.max_length:
            return
          apiurl = 'http://metamark.net/api/rest/simple'
          urlargs = urllib.urlencode({'long_url':url})
          tinyurl = urllib.urlopen(apiurl, urlargs).read()
          return tinyurl
        except Exception, error:
          log.exception(error)

    def response(self, nick, args, kwargs):
        try:
            log.info(args)
            query = args[0]
            result = self.tiny_url(query)
            if result:
                t = self.gettitle(query)
                if t:
                  return u'[ %s - %s ]' % (result, t)
                else:
                  return u'[ %s ]' % result

        except Exception, error:
            log.warn('error in module %s' % self.__module__)
            log.exception(error)


Main = Shorten


if __name__ == u'__main__':
    from include.utils import test_module
    test_module(Main)
