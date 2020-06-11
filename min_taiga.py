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
# Purpose: First minimal client object plus a smoke test using it.
#
# Design.: + Client class called from an embeded test case. 
#          + Manual validation.
#
# Author.: Fioddor Superconcentrado <fioddor@gmail.com>
#
#-----------------------------------------------------------------------------------------------------------------------------------------

import sys , requests        


SERVER = 'https://api.taiga.io/api/v1/'


class TaigaMinClient():
    '''Minimalistic Taiga Client.'''

    H_CT   = {'Content-Type': 'application/json'}
    headers=None

    def __init__(self, url=None, user=None, pswd=None):
        if not url or not user or not pswd:
            print('Faltan parámetros mínimos.')
        else:
            self.base_url = url
            self.user     = user
            self.pswd     = pswd
            print( 'Debug: Init ' + self.user + ':' + self.pswd + '@' + self.base_url )
     
    def login(self):
        '''Gets session token'''
        
        data_str = '{ ' + '"type": "normal", "username": "{}", "password": "{}"'.format( self.user , self.pswd ) + ' }'
        data_ba  = bytearray(data_str, encoding='utf-8')

        rs0 = requests.post( self.base_url+'auth' , data=data_ba , headers=self.H_CT )
         
        if 200==rs0.status_code:
            self.headers = self.H_CT
            self.headers['Authorization'] = 'Bearer ' + rs0.json()['auth_token']
            print(self.headers)
        else:
            print(rs0.request.body)
            print(rs0.status_code)
            print(rs0.text)
     
    def rq(self, branch):
        '''Most basic externally driven request handler.'''
        if not self.headers:
            self.login()
        return requests.get( self.base_url+branch, headers=self.headers)



if 3 != len(sys.argv):
    print( 'Required 2 args: user and pass. {} arguments passed. Aborting...'.format(len(sys.argv)-1) )
else:
    tmc = TaigaMinClient( SERVER , sys.argv[1] , sys.argv[2] )
     
    rs1 = tmc.rq('projects')
     
    print('/--- Rq#1: /projects:')
    print(rs1.headers)
    print(rs1.request.body)
    print(rs1.status_code)
    print(rs1.text)
    print('\n---')
    lst = rs1.json()
    print(len(lst))
    print('\\--- Rq#1.')

