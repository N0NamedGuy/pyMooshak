#!/usr/bin/env python2
#
# (C) 2011 David Miguel de Araujo Serrano
#
# This file is part of pyMooshak.
# 
# pyMooshak is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pyMooshak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyMooshak.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import os
import sys
import pycurl
from StringIO import StringIO

from BeautifulSoup import BeautifulSoup

class Mooshak:
    session = None
    base_url = None
    curl = None
    quote = ':./?=&'
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.COOKIEFILE, "")

    def _sink(self, buf):
        pass

    def _get_req_handler(self, req = "", data = None, headers = [],
        read_fun = None):

        self.curl.setopt(pycurl.URL, urllib.quote(
            self.base_url + 'cgi-bin/execute/' + req, self.quote))

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
        self.session = self.curl.getinfo(
            pycurl.EFFECTIVE_URL).split("/")[-1]

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

    def _guest_session(self, contest):
        self._new_session()

        data_dict = { 'contest': contest };
        self._get_req_handler(self.session + '?login',
            urllib.urlencode(data_dict))
        self._get_req_handler(self.session + '?guest')
        pass
        
        
    def _get_submission_response(self, html):
        soup = BeautifulSoup(html)
        h3 = soup.findAll("h3")[0].string;

        return h3

    def _get_submission_list(self, html):
        soup = BeautifulSoup(html)
        table = soup.findAll('table')[0]
        trows = table.findAll('tr')[1:]

        ret = []
        for row in trows:
            divs = row.findAll('td')

            dict = {}
            dict['number'] = divs[0].findAll('b')[0].string
            dict['time'] = divs[1].string
            dict['team'] = divs[3].findAll('font')[0].string 
            dict['problem'] = divs[4].findAll('font')[0].string 
            dict['language']= divs[5].string 
            dict['result']= divs[6].findAll('font')[0].string 
            dict['state']= divs[7].findAll('font')[0].string 

            ret.append(dict)

        return ret

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
        self._new_session()

        b = StringIO()
        self._get_req_handler(self.session + '?login', read_fun = b.write)
        
        soup = BeautifulSoup(b.getvalue())
        contest_sel = soup.findAll('select')[-1]
        contests_opt = contest_sel.findAll('option')

        ret = {}
        for opt in contests_opt[1:]:
            ret[opt['value']] = str(opt.string).rstrip()

        return ret        

    """
    Returns a dictionary of problems from a specified contest, in the current
    server.
    The key is the problem real name, the value is the problem description
    """
    def list_problems(self, contest): 
        self._guest_session(contest)
        b = StringIO()
        self._get_req_handler(self.session + '?vtools', read_fun=b.write)
        
        soup = BeautifulSoup(b.getvalue())
        selects = soup.findAll('select')
        probs_opt = selects[1].findAll('option') 

        ret = {}
        for opt in probs_opt:
            ret[opt['value']] = str(opt.string)
    
        return ret

    """
    Lists submissions made into a specific contest.
    """
    def list_submissions(self, contest, page=0, lines=5):
        self._guest_session(contest)

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
        
        return self._get_submission_list(b.getvalue())

    """
    Returns the last found result for a specified user on a specified contest
    """
    def get_last_result(self, contest, user, maxlines=100):
        subs = self.list_submissions(contest, 0, maxlines)
        
        for s in subs:

            suser = '_'.join(s['team'].split(' ')[1].split(' '))
            if suser == user:
                return s

        return None

pycurl.global_init(pycurl.GLOBAL_ALL) 

