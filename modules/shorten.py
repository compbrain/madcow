#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from htmlentitydefs import name2codepoint as n2cp

__version__ = '0.1'
__author__ = 'Will Nowak <wan@ccs.neu.edu>'
__all__ = []


def decode_htmlentities(string):
    """
    Decode HTML entities–hex, decimal, or named–in a string
    @see http://snippets.dzone.com/posts/show/4569

    >>> u = u'E tu vivrai nel terrore - L&#x27;aldil&#xE0; (1981)'
    >>> print decode_htmlentities(u).encode('UTF-8')
    E tu vivrai nel terrore - L'aldilà (1981)
    >>> print decode_htmlentities("l&#39;eau")
    l'eau
    >>> print decode_htmlentities("foo &lt; bar")
    foo < bar
    """
    def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
            # decoding by number
            if match.group(2) == '':
                # number is in decimal
                return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x'+ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else: return match.group()

    entity_re = re.compile(r'&(#?)(x?)(\w+);')
    return entity_re.subn(substitute_entity, string)[0]

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
            titlestr = decode_htmlentities(titlestr)
            titlestr = re.sub('(\s+)', ' ', titlestr)
            titlestr = titlestr.lstrip()
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
          assert tinyurl[:13] == 'http://xrl.us'
          assert len(tinyurl) < 30
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
