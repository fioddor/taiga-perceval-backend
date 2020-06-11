#!/usr/bin/env python3
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
# Purpose: Automatic unit tests for TaigaMinClient.
#
# Design.: - unittest as framework.
#          - API credentials read from a config file.
#          - More and better tests.
#          - Better verbosity.
#
# Authors:
#     Igor Zubiaurre <fioddor@gmail.com>
#
# Pending:
#   - situar en estructura de carpetas/módulos
#   - más TCs:
#     - rq
#       - token caducado => 301?
#       - token malo => 301?
#     - rq headers:
#       - paginación
#       - tiempo de token 
#     - rq paginadas/sin paginar
#   - más comandos:
#     - project/id
#     - project/id/stats
#     - backlog
#     - kanban
#     - wiki
#   - httpretty (mocking) para probar offline.
#   - #


import configparser , unittest

from min_taiga import TaigaMinClient


CFG_FILE = 'test_min_taiga.cfg'


class TestTaigaClient(unittest.TestCase):
    """Taiga API client tests"""

    API_URL = None
    API_USR = None
    API_PWD = None
    API_TKN = None    
     
     
    def setup_taiga(self):

        #sloppy testing fix:
        print('\n')  # after testCase name and description.
         
        # read config file:
        cfg = configparser.RawConfigParser()
        cfg.read( CFG_FILE )
         
        # take url:
        self.API_URL = cfg.get( 'taiga-site' , 'API_URL' )
         
        # take credentials (2 options):
        tag = 'taiga-default-credentials'
         
        has_usr_pwd = True
        try:
            self.API_USR = cfg.get( tag , 'User'     )
            self.API_PWD = cfg.get( tag , 'Password' )
            print( 'Debug: TestTaigaMinClient.setup_taiga has read user {}, pswd {}.'.format( self.API_USR , self.API_PWD ) )
        except KeyError(key):
            has_usr_pwd = False
         
        has_token = True
        try:
            self.API_TKN = cfg.get( tag , 'Token' )
            print( 'Debug: TestTaigaMinClient.setup_taiga has read token {}.'.format( self.API_TKN ) )
        except KeyError(key):
            has_token = False
         
        if not (has_usr_pwd or hastoken):
            raise Expception('TestTaigaMinClient.setup_taiga FAILED due to test data missing: credentials missing in test config file.')
         
         
    def test_init_without_expected_arguments_causes_exception(self):
        '''Raises Exception if client is requested without expected arguments.
        
        Either:
        a) url and token.
        b) url, user and pswd.
        '''
         
        self.setup_taiga()
         
        # Without arguments at all: 
        self.assertRaises( Exception , TaigaMinClient )
         
        # Only (valid) URL (missing either token or both, user and pswd):
        with self.assertRaises( Exception ):
            tmc = TaigaMinClient( url=self.API_URL ) 
         
        # Missing URL with user and pswd:
        with self.assertRaises( Exception ):
            tmc = TaigaMinClient( user=self.API_USR , pswd=self.API_PWD )

        # Missing URL with a (random) token:
        # (Tokens expire, we cannot staticly use a valid one)
        with self.assertRaises( Exception ):
            tmc = TaigaMinClient( token='some_clumsy_token' )
         
        # Missing user:
        with self.assertRaises( Exception ):
            tmc = TaigaMinClient( url=self.API_URL , pswd=self.API_PWD )
         
        # Missing pswd:
        with self.assertRaises( Exception ):
            tmc = TaigaMinClient( url=self.API_URL , user=self.API_USR )
     
     
    def test_init_with_token(self):
        '''A client created with a token has that token.'''
        a_token = 'a_clumsy_long_token'
        self.setup_taiga()
         
        tmc = TaigaMinClient( url=self.API_URL , token=a_token )
         
        self.assertEquals( tmc.get_token() , a_token )
         
         
    def test_init_with_usr_and_pswd(self):
        '''A client is created without token.'''
        self.setup_taiga()
         
        tmc = TaigaMinClient( url=self.API_URL , user=self.API_USR , pswd=self.API_PWD )
        self.assertEquals( None , tmc.get_token() )
         
         
    def test_initialization(self):
        '''Test initialization for Taiga testing.'''
        
        SAFE_API_COMMAND = 'projects'
        self.setup_taiga()
         
        # real init(implicit url, user, pswd) executes (no exception): 
        tmc = TaigaMinClient( self.API_URL , self.API_USR , self.API_PWD )
         
        # a fresh real init sets no token:
        self.assertEqual( None , tmc.get_token() )
         
        # ... and executes request (no exception):
        rs1 = tmc.rq(SAFE_API_COMMAND)

        self.assertEquals( 200 , rs1.status_code )
        lst = rs1.json()
        self.assertEquals( 30 , len(lst) )

        # ... now it has a (non-None) token:
        self.API_TKN = tmc.get_token()
        self.assertFalse( None == self.API_TKN ) 
         
         
        # a hybrid re-init (positional url, explicit token) executes (no exception):
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
        # and executes (the same valid) request (no exception):
        rs2 = tmc.rq(SAFE_API_COMMAND)
        self.assertEquals( 200 , rs2.status_code )
         
        
    def OFF_test_under_construction(self):
        '''This test is under construction.'''
         
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
        response = tmc.rq('new API command here')
         
        print( '/--- Rq:' )
        print( response.request.headers )
        print( response.request.body    )
        print( response.headers     )
        print( response.status_code )
        print( response.text[:100] + ' ...' )
        print( response.json )
        print( '\\--- Rq' )


print( '\n' * 3 )

if __name__ == "__main__":
    print( 'Debug: Executing test_taiga as __main__ (called as ./script.py or as python3 script.py).' )
    print( '-' * 40 )
    unittest.main(verbosity=3)
else:
    print( 'Debug: Executing test_taiga as "{}".'.format(__name__) )
    print( '-' * 40 )
