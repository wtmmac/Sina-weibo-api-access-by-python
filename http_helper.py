# -*- coding: utf-8 -*-
#/usr/bin/env python

import urllib2,cookielib


class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(cls, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(cls, req, fp, code, msg, headers)
        result.status = code
        print headers
        return result

    def http_error_302(cls, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(cls, req, fp, code, msg, headers)
        result.status = code
        print headers
        return result

def get_cookie():
    cookies = cookielib.CookieJar()
    return urllib2.HTTPCookieProcessor(cookies)

def get_opener(proxy=False):
    rv=urllib2.build_opener(get_cookie(), SmartRedirectHandler())
    rv.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)')]
    return rv