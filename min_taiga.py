# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Fioddor Superconcentrado
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
# Purpose: Minimal client in a library.
#
# Usage..: 1. Instantiate object from other python program with either
#             a) API token or
#             b) user and password
#          2. Only if you instantiated with user and password you need to (call) login.
#
# Design.: - Library with client class.
#          - Reusable user token.
#          - Asynchronous =>
#            - Close client sessions (pass them closed).
#            - Signal server to close HTTP session.
#            See https://stackoverflow.com/questions/10115126/python-requests-close-http-connection#15511852
#          - Paginates to completion or to requested maximum.
#
# Author.: Fioddor Superconcentrado <fioddor@gmail.com>
#
#-----------------------------------------------------------------------------------------------------------------------------------------

import requests
from math import ceil



class TaigaMinClient():
    '''Minimalistic Taiga Client.'''

    H_STANDARD_BASE = { 'Content-Type': 'application/json'
                      ,   'Connection': 'close'
                      }
     
    token   = None
    headers = None
     
     
    def __init__(self, url=None, user=None, pswd=None, token=None):
        if not url:
            raise Exception('Minimal argument url (Taiga API base URL) is missing.')
        self.base_url = url
        
        if token:
            self.token = token
            self.__set_headers__()
            print( 'Debug: TaigaMinClient.Init ' + self.token ) 
        elif not user or not pswd:
            raise Exception('Minimal arguments are missing: either token or user and pswd.')
        else:
            self.user = user
            self.pswd = pswd
            print( 'Debug: TaigaMinClient.Init ' + self.user + ':' + self.pswd +'@' + self.base_url )
     
     
    def get_token(self):
        '''Returns session token for reuse.'''
        return self.token
     
     
    def __set_headers__(self):
        '''(Re)sets session headers'''
         
        self.headers = self.H_STANDARD_BASE.copy()
        self.headers['Authorization'] = 'Bearer ' + self.token
        print( 'Debug: TaigaMinClient.__set_headers__ as ' + str(self.headers) )
     
     
    def login(self):
        '''Gets session token and (re)sets session headers accordingly'''
         
        data_str = '{ ' + '"type": "normal", "username": "{}", "password": "{}"'.format( self.user , self.pswd ) + ' }'
        data_ba  = bytearray(data_str, encoding='utf-8')
         
        rs0 = requests.post( self.base_url+'auth' , data=data_ba , headers=self.H_STANDARD_BASE )
        rs0.close() 
        
        if 200 == rs0.status_code:
            self.token = rs0.json()['auth_token']
            self.__set_headers__()
        else:
            me = 'Debug: TaigaMinClient.login'
            print( me + ' failed:'                                      )
            print( me + ' Rq.headers : '     + str(rs0.request.headers) )
            print( me + ' Rq.body : '        + str(rs0.request.body)    )
            print( me + ' Rs.status_code : ' + str(rs0.status_code )    )
            print( me + ' Rs.text:\n'        + rs0.text                 )
     
     
    def rq(self, branch):
        '''Most basic externally driven request handler.
        
        :returns: a closed requests response. The full object is returned
                  (whether successful or not) for further analysis. Only
                  raises an exception if the client is not initiated.
        '''
        if not self.headers:
            raise Exception( 'Client not yet initiated' )
        rs = requests.get( self.base_url+branch, headers=self.headers)
        rs.close()
        return rs
     
    
    def rq_pages(self, branch, max_pages=None):
        '''Generic request handler.
         
        :param max_pages: maximum number of pages to request. All pages, if
            this argument is missing.
        :returns: a list of Taiga JSON objects. Raises exceptions if anything
            fails.
        '''
        if not self.headers:
            raise Exception( 'Client not yet initiated.' )
         
        response = requests.get( self.base_url+branch, headers=self.headers )
        if 200 != response.status_code:
            raise Exception ( 'Http return code {} retrieving {}.'.format(response_status_code , self.base_url+branch) )
        else:
            output = response.json()
             
            if response.headers['x-paginated']:
                max_taiga = ceil( int(response.headers['x-pagination-count'])
                                / int(response.headers['x-paginated-by'])
                                )
                if max_pages:
                    maximum = min([ max_pages , max_taiga ])
                else:
                    maximum = max_taiga
                 
                while int(response.headers['x-pagination-current']) < maximum:
                    next_url = response.headers['X-Pagination-Next']
                    response = requests.get( next_url , headers=self.headers )
                    if 200 != response.status_code:
                        print( response.headers )
                        raise Exception( 'Http return code {} retrieving {}.'.format(response.status_code , next_url) )
                    else:
                        # print( response.headers )
                        output.extend( response.json() )
                        print( 'Debug.TaigaMinClient.rp_pages got yet {} items out of {}.'.
                               format( len(output) , response.headers['x-pagination-count'] )
                             )
             
            response.close()
            return output
     
     
    def proj_stats(self, project):
        '''Retrieve some basic stats from the given project.'''
        response = self.rq( 'projects/{}/stats'.format(project) )
        if 200==response.status_code:
            record = response.json()
            output = { "pjId":str(project) }
            for datum in [ 'total_milestones' , 'total_points' , 'closed_points' , 'defined_points' , 'assigned_points' ]:
                output[datum] = record[datum]
            return output
        else:
            raise Exception( "TaigaClient failure: This shoudn't have happened!" )
     
     
    def proj_issues_stats(self, project):
        '''Retrieve some basic issues_stats from the given project.'''
        response = self.rq( 'projects/{}/issues_stats'.format(project) )
        if 200==response.status_code:
            record = response.json()
            output = { "pjId":str(project) }
            for datum in [ 'total_issues' , 'opened_issues' , 'closed_issues' , 'issues_per_priority' , 'issues_per_severity' , 'issues_per_status' ]:
                output[datum] = record[datum]
            return output
        else:
            raise Exception( "TaigaClient failure: This shoudn't have happened!" )


