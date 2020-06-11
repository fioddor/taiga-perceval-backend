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
# Usage..: Call from other python program.
#
# Design.: - Library with client class.
#          - Reusable token.
#          - Asynchronous =>
#            - Close client sessions (pass them closed).
#            - Signal server to close HTTP session.
#            See https://stackoverflow.com/questions/10115126/python-requests-close-http-connection#15511852
#
# Author.: Fioddor Superconcentrado <fioddor@gmail.com>
#
#-----------------------------------------------------------------------------------------------------------------------------------------

import requests        



class TaigaMinClient():
    '''Minimalistic Taiga Client.'''

    H_STANDARD_BASE = { 'Content-Type': 'application/json'
                      ,   'Connection': 'close'
                      }
    token = None
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
        '''Most basic externally driven request handler.'''
        if not self.headers:
            self.login()
        rs = requests.get( self.base_url+branch, headers=self.headers)
        rs.close()
        return rs


