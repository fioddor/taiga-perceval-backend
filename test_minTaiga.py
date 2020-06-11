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
#       - tiempo de token 
#   - más comandos:
#   - httpretty (mocking) para probar offline.
#   - #


import configparser , unittest

from min_taiga import TaigaMinClient


CFG_FILE = 'test_minTaiga.cfg'


class TestTaigaClient(unittest.TestCase):
    """Taiga API client tests"""

    API_URL = None
    API_USR = None
    API_PWD = None
    API_TKN = None    
     
    TST_CFG = None
     
     
    def setup_taiga(self):
        '''Set up Taiga service'''
         
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
         
        # load other test data:
        self.TST_CFG = cfg
         
         
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


    def test_pj_stats(self):
        '''Taiga Project Stats'''
          
        def td( var_name ):
            return self.TST_CFG.get( 'test-data' , var_name )
         
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
        record = tmc.proj_stats( td( 'proj_stats_id' ) )
         
        field_names = [ 'total_milestones' , 'defined_points' , 'assigned_points' , 'closed_points' ]
        for field in field_names:
             self.assertGreaterEqual( record[field] , float(td( 'proj_stats_min_'+field )) )
     
     
    def test_pj_issues_stats(self):
        '''Taiga Project Issues Stats'''
         
        def td( var_name ):
            return self.TST_CFG.get( 'test-data' , var_name )
         
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
        record = tmc.proj_issues_stats( td( 'proj_issues_stats_id' ) )
        field_names = [ 'total_issues' , 'opened_issues' , 'closed_issues' ]
        for field in field_names:
            self.assertGreaterEqual( record[field] , float(td( 'proj_issues_stats_min_'+field )) )
         
        group_names = [ 'priority' , 'severity' , 'status' ]
        for group in group_names:
            self.assertGreaterEqual( len(record['issues_per_'+group]) , float(td( 'proj_issues_stats_min_per_'+group )) )
         
         
    def __test_pj_list__(self, list_name):
        '''Standard test for Taiga Project List-property'''
         
        def td( var_name ):
            return self.TST_CFG.get( 'test-data' , var_name )
         
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
        
        project_id = td( 'proj_{}_id'.format( list_name ) )
        json_list = tmc.rq_pages( '{}?project={}'.format( list_name , project_id ) )
        #print( response.headers )
        #json_list = response.json()
        item_count = len(json_list)
        print( '{} {} items found.'.format( item_count , list_name ) )
        # print( 'RS:'+str(json_list) )
         
        min_name = 'proj_{}_min'.format( list_name )
        self.assertGreaterEqual( item_count , float(td( min_name )) )
     
     
    def test_pj_epics(self):
        '''Taiga Project Epics.'''
        return self.__test_pj_list__( 'epics' )
     
     
    def test_pj_userstories(self):
        '''Taiga Project User Stories.'''
        return self.__test_pj_list__( 'userstories' )
     
     
    def test_pj_tasks(self):
        '''Taiga Project Tasks.'''
        return self.__test_pj_list__( 'tasks' )
     
     
    def test_pj_wiki_pages(self):
        '''Taiga Project Wiki Pages.'''
        return self.__test_pj_list__( 'wiki' )
     
     
    def test_command(self):
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
        response1 = tmc.rq('projects')
        if 200 != response1.status_code:
            self.fail( "Coudn't test projects/id/stats because the request for project list failed." )
            return
        lst = response1.json()
        print( str(len(lst)) + ' projects found.' )
        for pj in lst:
            command_under_test = 'wiki?project={}'.format( pj['id'] )
            response = tmc.rq(command_under_test)
             
            if 200==response.status_code:
                rec = response.json()
                num = len(rec)
                if 0 < num:
                    print( str(pj['id']) + ' has ' + str(len(rec)) + ' wiki pages.' )
                    # print(str(rec))
        return
         
         
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
