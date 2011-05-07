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
import os
import sys
import pycurl
from StringIO import StringIO

from BeautifulSoup import BeautifulSoup

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

    def _sink(self, buf):
        pass

    def _get_req_handler(self, req = "", data = None, headers = [],
        read_fun = None):

        self.curl.setopt(pycurl.URL, urllib.quote(
            self.base_url + 'cgi-bin/execute/' + req, self.quote))

        print urllib.quote(
            self.base_url + 'cgi-bin/execute/' + req, self.quote)

        if read_fun != None: 
            self.curl.setopt(pycurl.WRITEFUNCTION, read_fun)
        else:
            self.curl.setopt(pycurl.WRITEFUNCTION, self._sink)

        if data != None:
            self.curl.setopt(pycurl.POST, 1)
            self.curl.setopt(pycurl.POSTFIELDS, data)
        else:
            self.curl.setopt(pycurl.POST, 0)
        
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        self.curl.perform()

    def _new_session(self):
        if self.session != None:
            return

        self.curl.setopt(pycurl.URL, urllib.quote(
            self.base_url + 'cgi-bin/execute', self.quote))

        self.curl.setopt(pycurl.WRITEFUNCTION, self._sink)
        self.curl.setopt(pycurl.POST, 0)
        self.curl.setopt(pycurl.FOLLOWLOCATION, 1)

        self.curl.perform()
        self.session = self.curl.getinfo(pycurl.EFFECTIVE_URL).split("/")[-1]

    def _login(self, contest, user, password):
        if (self.session == None):
            self._new_session();

        # Do the actual login
        data_dict = {}
        data_dict['command'] = 'login'
        data_dict['arguments'] = ''
        data_dict['contest'] = contest
        data_dict['user'] = user
        data_dict['password'] = password
        
        
        self._get_req_handler(self.session,
            urllib.urlencode(data_dict)); 
        
    def _get_submission_response(self, html):
        soup = BeautifulSoup(html)
        h3 = soup.findAll("h3")[0].string;

        return h3

    """
    Submits a solution. Returns a string containing the submissions result.
    Note that to know if the submission was accepted (or not), you must
    call get_last_result()
    """
    def submit(self, contest, user, password, problem, file_path):

        self._login(contest, user, password)

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

        b = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, b.write)
        self.curl.perform()
        
        return self._get_submission_response(b.getvalue())

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
    Lists submissions made into a specific contest.
    """
    def list_submissions(self, contest, page=0, lines=5):
        self._new_session()
        self._get_req_handler(self.session + '?login', 'contest=%s&user=&password=')
        self._get_req_handler(self.session + '?guest')

        b = StringIO()
        data = ('all_problems=on' +
                '&page=' + str(int(page)) +
                '&all_teams=on' +
                '&type=submissions' +
                '&lines=' + str(int(lines)) +
                '&time=0' +
                '&command=listing')

        self._get_req_handler(self.session + '?split', data)
        self._get_req_handler(self.session + '?' + data,
            read_fun = b.write)
        
        print b.getvalue()


        return None

    """
    Returns the last found result for a specified user on a specified contest
    """
    def get_last_result(self, contest, user):
        return ""

pycurl.global_init(pycurl.GLOBAL_ALL) 

