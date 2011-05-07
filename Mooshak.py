#!/usr/bin/env python2

####
# 05/2011 David Serrano <david.nonamedguy@gmail.com>
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#

import urllib
import urllib2
import httplib
import cookielib
import mimetypes
import mimetools
import os
import sys
import sys
import json
import itertools

import pycurl
import StringIO

from BeautifulSoup import BeautifulSoup
from MultipartPostHandler import MultipartPostHandler

# TODO: out with URLLIB in with PYCURL
# TODO: further reading: http://pycurl.sourceforge.net/

class MooshakError(Exception):
    pass

class NotLoggedIn(MooshakError):
    pass

class WrongPassword(MooshakError):
    pass

class LoggedIn(MooshakError):
    pass 

class Mooshak:
    contest = None
    session = None
    base_url = None
    curl = None
    quote = ':./?=&'
    cookie_file = "moo_cookies.txt"
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.COOKIEFILE, self.cookie_file)
        self.curl.setopt(pycurl.COOKIEJAR, self.cookie_file)
        pass

    def _sink(self, buf):
        pass

    def _get_req_handler(self, req = "", data = None, headers = [], read_fun = None):

        self.curl.setopt(pycurl.URL, urllib.quote(
            self.base_url + 'cgi-bin/execute/' + req, self.quote))
       
        if read_fun != None: 
            self.curl.setopt(pycurl.WRITEFUNCTION, read_fun)
        else:
            self.curl.setopt(pycurl.WRITEFUNCTION, self._sink)

        if data != None:
            self.curl.setopt(pycurl.POST, 1)
            self.curl.setopt(pycurl.POSTFIELDS, data)
        
        self.curl.setopt(pycurl.HTTPHEADER, headers)

        self.curl.perform()

    def _new_session(self):
        self.curl.setopt(pycurl.URL, urllib.quote(
            self.base_url + 'cgi-bin/execute', self.quote))

        self.curl.setopt(pycurl.WRITEFUNCTION, self._sink)

        self.curl.setopt(pycurl.FOLLOWLOCATION, 1)
        self.curl.perform()
        self.session = self.curl.getinfo(pycurl.EFFECTIVE_URL).split("/")[-1]

    """
    Returns a dictionary of contests in the current server.
    The key is the contest real name, the value is the contest description
    """
    def list_contests(self):
        return {}

    """
    Returns a dictionary of problems from a specified contest, in the current
    server.
    The key is the problem real name, the value is the problem description
    """
    def list_problems(self, contest, problem): 
        return {}

    """
    Logs into the mooshak server, using the current configuration.
    """
    def login(self, contest, user, password):
        if (self.session == None):
            self._new_session();
        else:
            raise LoggedIn

        # Do the actual login
        data_dict = {}
        data_dict['command'] = 'login'
        data_dict['arguments'] = ''
        data_dict['contest'] = contest
        data_dict['user'] = user
        data_dict['password'] = password
        
        
        self._get_req_handler(self.session,
            urllib.urlencode(data_dict)); 
        
    """
    Logs out from the mooshak server.
    """
    def logout(self):
        if self.session == None:
            raise NotLoggedIn


        self.session = None
        

    """
    Submits a solution. Returns a string containing the submissions result.
    """
    def submit(self, contest, problem, file_path):

        if (self.session == None):
            raise NotLoggedIn

        params = { 'command': 'analyze',
                   'problem': problem,
                   'program' : file(file_path, 'rb'),
                   'analyze':'Submit'
        }

        self.curl.setopt(pycurl.URL, urllib.quote(
            self.base_url + 'cgi-bin/execute/' + self.session, self.quote))

        self.curl.setopt(pycurl.HTTPPOST, [
            ('command', 'analyze'),
            ('problem', problem),
            ('program', (self.curl.FORM_FILE, file_path)),
            ('analyze', 'Submit')])

        self.curl.setopt(pycurl.WRITEFUNCTION, self._sink)
        self.curl.perform()

        return "Wrong Answer"

    """
    Lists submissions made into a specific contest.
    """
    def list_submissions(self, contest, page=0, lines=5):
        return None

pycurl.global_init(pycurl.GLOBAL_ALL) 

