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
import json
import itertools

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
    cfg = {}
    session = None
    cj = cookielib.LWPCookieJar()

    def __init__(self, cfg):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)
        self.cfg = cfg

    def _get_req_handler(self, req = "", data = None, headers = {}):
        req = urllib2.Request(self.cfg['baseurl'] + '/cgi-bin/execute/' + req,
            data, headers)
        handle = urllib2.urlopen(req)
        return handle;


    def _new_session(self):
        req = urllib2.Request(self.cfg['baseurl'] + '/cgi-bin/execute')
        handle = urllib2.urlopen(req)
        url = handle.geturl()
        self.session = url.split('/')[-1]

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
    def login(self):
        if (self.session == None):
            self._new_session();
        else:
            raise LoggedIn

        # Do the actual login
        data_dict = {}
        data_dict['command'] = 'login'
        data_dict['arguments'] = ''
        data_dict['contest'] = self.cfg['contest']
        data_dict['user'] = self.cfg['user']
        data_dict['password'] = self.cfg['password']
        
        handle = self._get_req_handler(self.session,
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
        # TODO: The parameters MUST be sent in the "order" specified in params.
        # TODO: Find a way to deal with binary data


        if (self.session == None):
            raise NotLoggedIn

        params = { 'command': 'analyze',
                   'problem': problem,
                   'program' : file(file_path, 'rb'),
                   'analyze':'Submit'
        }
        opener = urllib2.build_opener(MultipartPostHandler)
        h = opener.open(self.cfg['baseurl'] + "cgi-bin/execute/" + self.session, params)
        print h.read()

        return "Wrong Answer"

    """
    Lists submissions made into a specific contest.
    """
    def list_submissions(self, contest, page=0, lines=5):
        return None



