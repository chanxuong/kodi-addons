# -*- coding: utf-8 -*-
import urllib
import requests
import xbmcgui
import sys, traceback
from Queue import Queue
from threading import Thread

user_agent = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/59.0.3071.115 Safari/537.36"
)


class Request:
    TIMEOUT = 60

    DEFAULT_HEADERS = {
        'User-Agent': user_agent
    }
    session = None
    r = None

    def __init__(self, header=None, session=True, cookies=None):
	
        if header:
            self.DEFAULT_HEADERS = header
        if session:
            self.session = requests.session()
        if cookies:
            self.session = requests.session()
            self.session.cookies.update(cookies)
		

    def get(self, url, headers=None, params=None, redirect=True, cookies=None, verify=True):
        print("Request URL: %s" % url)
        if not headers:
            headers = self.DEFAULT_HEADERS
        if self.session:
            self.r = self.session.get(url, headers=headers, timeout=self.TIMEOUT, params=params,
                                      allow_redirects=redirect, cookies=cookies, verify=verify)
        else:
            self.r = requests.get(url, headers=headers, timeout=self.TIMEOUT, params=params, allow_redirects=redirect,
                                  cookies=cookies)
        return self.r.text

    def post(self, url, params=None, headers=None, redirect=True, cookies=None, json=None, verify=True):
        try:
            print("Post URL: %s params: %s" % (url, urllib.urlencode(params)))
        except:
            pass
        if not headers:
            headers = self.DEFAULT_HEADERS

        print("Post URL: %s header: %s" % (url, urllib.urlencode(headers)))
        if self.session:
            self.r = self.session.post(url, data=params, headers=headers, timeout=self.TIMEOUT,
                                       allow_redirects=redirect, cookies=cookies, json=json, verify=verify)
            # for resp in self.r.history:
            #     print(resp.status_code, resp.url)
        else:
            self.r = requests.post(url, data=params, headers=headers, timeout=self.TIMEOUT, allow_redirects=redirect,
                                   cookies=cookies, json=json)
        return self.r.text

    def head(self, url, params=None, headers=None, redirect=True, cookies=None, verify=True):
        if not headers:
            headers = self.DEFAULT_HEADERS
        if self.session:
            self.r = self.session.head(url, headers=headers, timeout=self.TIMEOUT, params=params,
                                       allow_redirects=redirect, verify=verify)
        else:
            self.r = requests.head(url, headers=headers, timeout=self.TIMEOUT, params=params, allow_redirects=redirect)
        return self.r

    def options(self, url, params=None, headers=None, redirect=True, cookies=None, verify=True):
        # if headers:
        #     headers = self.DEFAULT_HEADERS.update(headers)
        if self.session:
            self.r = self.session.options(url, headers=headers, timeout=self.TIMEOUT, params=params,
                                          allow_redirects=redirect, verify=verify)
        else:
            self.r = requests.options(url, headers=headers, timeout=self.TIMEOUT, params=params,
                                      allow_redirects=redirect)
        return self.r

    def set_session(self, session):
        self.session = session

    def get_request_session(self):
        return self.session

    def get_request(self):
        return self.r
	
		
		
		