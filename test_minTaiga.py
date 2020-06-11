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
# Design.: - Unittest as framework.
#          - More and better tests:
#            - Some tests reuse the new default client.
#          - Better verbosity.
#
# Authors:
#     Igor Zubiaurre <fioddor@gmail.com>
#
# Pending:
#   - Complete mocked tests.
#   - Integrate into perceval structure.
#   - More TCs:
#     - Expired token => HTTP 301?
#   - readfile shold be shared with gitlab (remove when integrating and ask for it to be moved).
#


import unittest                       # common usage.
import configparser                   # for TestTaigaClientAgainstRealServer.
import httpretty as mock, os          # for TestTaigaClientAgainstMockServer.

from min_taiga import TaigaMinClient  # common usage.


CFG_FILE = 'test_minTaiga.cfg'



class TestTaigaClientAgainstRealServer(unittest.TestCase):
    """Taiga API client tests against a real Taiga server.

    Design:
    - Test data are read from a config file.
    - Setup creates a default client to be reused.
    """
     
    # Configured test data to be passed from common setup to testcases:
    API_URL = None
    API_USR = None
    API_PWD = None
    API_TKN = None    
     
    TST_CFG = None   # Configured test data.
    TST_DTC = None   # Default Taiga Client for testing.
     
     
    def setup_taiga(self):
        '''Set up Taiga service'''
         
        #sloppy testing fix:
        print('\n')  # after testCase name and description.
        
        # clean up common test data:
        self.API_URL = None
        self.API_USR = None
        self.API_PWD = None
        self.API_TKN = None
        self.TST_CFG = None
        self.TST_DTC = None
         
        # read config file:
        cfg = configparser.RawConfigParser()
        cfg.read( CFG_FILE )
         
        # take url:
        self.API_URL = cfg.get( 'taiga-site' , 'API_URL' )
         
        # take credentials (2 options):
        tag = 'taiga-default-credentials'
         
        try:
            self.API_USR = cfg.get( tag , 'User'     )
            self.API_PWD = cfg.get( tag , 'Password' )
            has_usr_pwd = True
            # print( 'Debug: TestTaigaMinClient.setup_taiga has read user {}, pswd {}.'.format( self.API_USR , self.API_PWD ) )
        except KeyError(key):
            has_usr_pwd = False
         
        try:
            self.API_TKN = cfg.get( tag , 'Token' )
            has_token = True
            # print( 'Debug: TestTaigaMinClient.setup_taiga has read token {}.'.format( self.API_TKN ) )
        except KeyError(key):
            has_token = False
         
        if not (has_usr_pwd or hastoken):
            raise Exception('TestTaigaMinClient.setup_taiga FAILED due to test data missing: credentials missing in test config file.')
         
        # load other test data:
        self.TST_CFG = cfg
        if has_token:
            self.TST_DTC = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
     
     
    def test_init_with_user_and_pswd(self):
        '''A client is created without token.
        
        Design:
        - Data used in client init doesn't affect this requirement. This testcase inits it
          with valid data (checked in other testcases). A similar testcase tests this with
          invalid data.
        '''
        self.setup_taiga()
         
        tmc = TaigaMinClient( url=self.API_URL , user=self.API_USR , pswd=self.API_PWD )
        self.assertEqual( None , tmc.get_token() )
         
         
    def test_initialization(self):
        '''Test Taiga Client initializations.'''
         
        SAFE_API_COMMAND = 'projects'
        self.setup_taiga()
         
        # user&pswd init(implicit url, user, pswd) executes (no exception): 
        tmc = TaigaMinClient( self.API_URL , self.API_USR , self.API_PWD )
         
        # a fresh user&pswd init sets no token:
        self.assertEqual( None , tmc.get_token() )
         
        # ... thus, it raises exception if executed before login():
        with self.assertRaises( Exception ):
            tmc.rq(SAFE_API_COMMAND)
         
        # ... but after login it executes a request (no exception):
        tmc.login()
        rs1 = tmc.rq(SAFE_API_COMMAND)
         
        self.assertEqual( 200 , rs1.status_code )
        
        # API returns max 30 items per page: (get limit from response header?)
        lst = rs1.json()
        self.assertEqual( 30 , len(lst) )
         
        # ... now it has a (non-None) token:
        fresh_token = tmc.get_token()
        self.assertFalse( None == fresh_token )
        # ... a brand new one:
        self.assertNotEqual( self.API_TKN , fresh_token )
         
        # a token re-init (url, explicit token) executes (no exception):
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
        # its token has changed as requested in the init command:
        self.assertEqual( self.API_TKN , tmc.get_token() )
        # and executes (the same valid) request (no exception):
        rs2 = tmc.rq(SAFE_API_COMMAND)
        self.assertEqual( 200 , rs2.status_code )
         
         
    def test_wrong_token(self):
        '''Taiga rejects wrong tokens.
         
        Taiga's response to a wrong token causes no exception.
        '''
        SAFE_API_COMMAND = 'projects'
        EXPECTED_RS_JSON = {"_error_message": "Invalid token", "_error_type": "taiga.base.exceptions.NotAuthenticated"} 
        self.setup_taiga()
         
        tmc = TaigaMinClient( url=self.API_URL , token='wrong_token' )
        response = tmc.rq( SAFE_API_COMMAND )
         
        self.assertEqual( 401 , response.status_code )
        self.assertDictEqual( EXPECTED_RS_JSON , response.json() )
         
         
    def test_pj_stats(self):
        '''Taiga Project Stats'''
          
        def td( var_name ):
            return self.TST_CFG.get( 'test-data' , var_name )
         
        self.setup_taiga()
         
        record = self.TST_DTC.proj_stats( td( 'proj_stats_id' ) )
         
        field_names = [ 'total_milestones' , 'defined_points' , 'assigned_points' , 'closed_points' ]
        for field in field_names:
             self.assertGreaterEqual( record[field] , float(td( 'proj_stats_min_'+field )) )
     
     
    def test_pj_issues_stats(self):
        '''Taiga Project Issues Stats'''
         
        def td( var_name ):
            return self.TST_CFG.get( 'test-data' , var_name )
         
        self.setup_taiga()
         
        record = self.TST_DTC.proj_issues_stats( td( 'proj_issues_stats_id' ) )
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
         
        project_id = td( 'proj_{}_id'.format( list_name ) )
        json_list = self.TST_DTC.rq_pages( '{}?project={}'.format( list_name , project_id ) )
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
     
     
    def OFF_test_proj_export(self):

        '''Taiga export doesn't work due to permissions.'''
         
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
        response = tmc.rq('exporter/156665')
         
        if 403 != response.status_code:
            print(response.json)
        self.assertEqual( 403 , response.status_code )
        self.assertEqual( 'You do not have permission to perform this action.' , response.json()['_error_message'] )
         
          
    def test_proj(self):
        '''Taiga Project data.
        
        Pending: Improve assert.
        '''
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
        
        data = tmc.proj(156665)
        print( str(len(data)) + ' project data items.' )
        print( len(str(data)) + ' bytes of size.'      )
        self.assertTrue(True)
     
     
    def OFF_test_command(self):
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
        response1 = tmc.rq('projects?is_backlog_activated=true&is_kanban_activated=true')
        if 200 != response1.status_code:
            print( response1.headers )
            print( response1 )
            self.fail( "Coudn't test projects/id/stats because the request for project list failed." )
            return
        lst = response1.json()
        print( str(len(lst)) + ' projects found.' )
        print( response1.headers )
        print( lst )
        return
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



def read_file(filename, mode='r'):
    '''Taken from test_gitlab.

    Pending: 1. remove (import instead)  when integrated with perceval.
             2. ask for it to be moved to a common place.
    '''
    with open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content



class TestTaigaClientAgainstMockServer(unittest.TestCase):
    """Taiga API client tests against a mock Taiga server.

    Design.: - Setup creates a default client to be reused.
    Pending: - Complete pending test_cases. 
    """
     
    # Configured test data to be passed from common setup to testcases:
    API_URL = None
    API_TKN = None    
     
    TST_DTC = None   # Default Taiga Client for testing.
     
     
    def setup_taiga(self):
        '''Set up Taiga service'''
         
        #sloppy testing fix:
        print('\n')  # after testCase name and description.
        
        # clean up common test data:
        self.API_URL = 'https://a.taiga.instance/API/V9/'
        self.API_TKN = 'a_clumsy_token'
        self.TST_DTC = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
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
        with self.assertRaises( Exception , msg='A TiagaClient init missing token or user or pswd should have raised an Exception.'):
            tmc = TaigaMinClient( url=self.API_URL ) 
         
        # Missing URL with user and pswd:
        with self.assertRaises( Exception , msg='A TaigaClient init missing the url should have raised an Exception.'):
            tmc = TaigaMinClient( user=self.API_USR , pswd=self.API_PWD )

        # Missing URL with a (random) token:
        with self.assertRaises( Exception , msg='A TaigaClient init missing the url should have raised an Exception.'):
            tmc = TaigaMinClient( token='some_clumsy_token' )
         
        # Missing user:
        with self.assertRaises( Exception , msg='A TaigaClient init missing the user should have raised an Exception'):
            tmc = TaigaMinClient( url=self.API_URL , pswd=self.API_PWD )
         
        # Missing pswd:
        with self.assertRaises( Exception , msg='A TaigaClient init missing the pswd should have raised an Exception.'):
            tmc = TaigaMinClient( url=self.API_URL , user=self.API_USR )
     
     
    def test_init_with_token(self):
        '''A client created with a token has that token.'''
        a_token = 'a_clumsy_long_token'
        self.setup_taiga()
         
        tmc = TaigaMinClient( url=self.API_URL , token=a_token )
         
        self.assertEqual( tmc.get_token() , a_token )
         
         
    def test_init_with_user_and_pswd(self):
        '''A client is created without token.
        
        Client init doesn't immediately connect to API. This would fail later on, at login.
        '''
        self.setup_taiga()
         
        tmc = TaigaMinClient( url=self.API_URL , user='a_random_user' , pswd='an_invalid_password' )
        self.assertEqual( None , tmc.get_token() )
         
         
    @mock.activate
    def test_initialization(self):
        '''Test Taiga Client initializations.'''
         
        SAFE_API_COMMAND = 'projects'
        self.setup_taiga()
        mock.register_uri( mock.GET
                         , self.API_URL + SAFE_API_COMMAND
                         , body=read_file('data/taiga/projects.body.RS')
                         , status=200
                         )
        mock.register_uri( mock.POST
                         , self.API_URL + 'auth'
                         , body='{ "auth_token":"a_token" }'
                         , status=200
                         )

        # user&pswd init(implicit url, user, pswd) executes (no exception): 
        tmc = TaigaMinClient( self.API_URL , 'a_user' , 'a_password' )
         
        # a fresh user&pswd init sets no token:
        self.assertEqual( None , tmc.get_token() )
         
        # ... thus, it raises exception if executed before login():
        with self.assertRaises( Exception ):
            tmc.rq(SAFE_API_COMMAND)
         
        # ... but after login it executes a request (no exception):
        tmc.login()
        rs1 = tmc.rq(SAFE_API_COMMAND)
         
        self.assertEqual( 200 , rs1.status_code )
        
        # API returns max 30 items per page: (get limit from response header?)
        lst = rs1.json()
        self.assertEqual( 30 , len(lst) )
         
        # ... now it has a (non-None) token:
        fresh_token = tmc.get_token()
        self.assertFalse( None == fresh_token )
        # ... a brand new one:
        self.assertNotEqual( self.API_TKN , fresh_token )
         
        # a token re-init (url, explicit token) executes (no exception):
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
        # its token has changed as requested in the init command:
        self.assertEqual( self.API_TKN , tmc.get_token() )
        # and executes (the same valid) request (no exception):
        rs2 = tmc.rq(SAFE_API_COMMAND)
        self.assertEqual( 200 , rs2.status_code )
         
         
    def PTE_test_wrong_token(self):
        '''Taiga rejects wrong tokens.'''
        SAFE_API_COMMAND = 'projects'
        EXPECTED_RS_JSON = {"_error_message": "Invalid token", "_error_type": "taiga.base.exceptions.NotAuthenticated"} 
        self.setup_taiga()
         
        tmc = TaigaMinClient( url=self.API_URL , token='wrong_token' )
        response = tmc.rq( SAFE_API_COMMAND )
         
        self.assertEqual( 401 , response.status_code )
        self.assertDictEqual( EXPECTED_RS_JSON , response.json() )
         
         
    @mock.activate
    def test_pj_stats(self):
        '''proj_stats retrieves the expected elements.
         
        None should be missing. No extra item should be dragged along.
        '''
         
        TST_PROJECT       = 'proj_id'
        TST_EXTRA_ITEM    = 'extra_item'
        TST_RESPONSE_BODY = {    TST_EXTRA_ITEM : 'Do NOT load me!'
                            , 'total_milestones': 111
                            ,   'defined_points': 333
                            ,  'assigned_points': 444
                            ,   'closed_points' : 555
                            ,    'total_points' : 666
                            }
         
        self.setup_taiga()
        mock.register_uri( mock.GET
                         , '{}projects/{}/stats'.format( self.API_URL , TST_PROJECT )
                         , status=200
                         , body=str(TST_RESPONSE_BODY).replace( "'" , '"' )
                         )
         
        record = self.TST_DTC.proj_stats( TST_PROJECT )
         
        # no expected value is missing:
        expected_field_names = TST_RESPONSE_BODY.keys() - [TST_EXTRA_ITEM]
        for field in expected_field_names:
            self.assertEqual( record[field] , TST_RESPONSE_BODY[field] )
         
        # no unexpected item is present:
        with self.assertRaises( KeyError , msg='TaigaClient.pj_stats is reading unwanted items!'):
            bah = record[TST_EXTRA_ITEM]
     
    @mock.activate 
    def test_pj_issues_stats(self):
        '''proj_issues_stats retrieves the expected elements.
        
        None should be missing. No extra item should be dragged along.
        '''

        TST_PROJECT       = 'proj_id'
        TST_EXTRA_ITEM    = 'extra_item'
        TST_RESPONSE_BODY = {        TST_EXTRA_ITEM : 'Do NOT load me!'
                            ,        'total_issues' : 55
                            ,       'opened_issues' : 22
                            ,       'closed_issues' : 33
                            , 'issues_per_priority' : ['prio1','prio2','prio3']
                            , 'issues_per_severity' : ['sev1','sev2','sev3','sev4']
                            , 'issues_per_status'   : ['status1','status2']
                            }
         
        self.setup_taiga()
        mock.register_uri( mock.GET
                         , '{}projects/{}/issues_stats'.format( self.API_URL , TST_PROJECT )
                         , status=200
                         , body=str(TST_RESPONSE_BODY).replace( "'" , '"' )
                         )
         
        record = self.TST_DTC.proj_issues_stats( TST_PROJECT )
         
        field_names = [ 'total_issues' , 'opened_issues' , 'closed_issues' ]
        for field in field_names:
            self.assertEqual( record[field] , TST_RESPONSE_BODY[field] )
         
        group_names = [ 'priority' , 'severity' , 'status' ]
        for group in group_names:
            field = 'issues_per_'+group
            self.assertFalse( set(record[field]) - set(TST_RESPONSE_BODY[field]) )
         
         
    def __test_pj_list__(self, list_name):
        '''Standard test for Taiga Project List-property'''
         
        def td( var_name ):
            return self.TST_CFG.get( 'test-data' , var_name )
         
        self.setup_taiga()
         
        project_id = td( 'proj_{}_id'.format( list_name ) )
        json_list = self.TST_DTC.rq_pages( '{}?project={}'.format( list_name , project_id ) )
        #print( response.headers )
        #json_list = response.json()
        item_count = len(json_list)
        print( '{} {} items found.'.format( item_count , list_name ) )
        # print( 'RS:'+str(json_list) )
         
        min_name = 'proj_{}_min'.format( list_name )
        self.assertGreaterEqual( item_count , float(td( min_name )) )
     
     
    def PTE_test_pj_epics(self):
        '''Taiga Project Epics.'''
        return self.__test_pj_list__( 'epics' )
     
     
    def PTE_test_pj_userstories(self):
        '''Taiga Project User Stories.'''
        return self.__test_pj_list__( 'userstories' )
     
     
    def PTE_test_pj_tasks(self):
        '''Taiga Project Tasks.'''
        return self.__test_pj_list__( 'tasks' )
     
     
    def PTE_test_pj_wiki_pages(self):
        '''Taiga Project Wiki Pages.'''
        return self.__test_pj_list__( 'wiki' )
     
     
    def PTE_test_403(self):
        
        '''Taiga export doesn't work due to permissions.'''
         
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
        response = tmc.rq('exporter/156665')
         
        if 403 != response.status_code:
            print(response.json)
        self.assertEqual( 403 , response.status_code )
        self.assertEqual( 'You do not have permission to perform this action.' , response.json()['_error_message'] )
         
          
    def PTE_test_proj(self):
        '''Taiga Project data.'''
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
        
        data = tmc.proj(156665)
        print( str(len(data)) + ' project data items.' )
        print( len(str(data)) + ' bytes of size.'      )
        self.assertTrue(True)
     
     
    def OFF_test_command(self):
        self.setup_taiga()
        tmc = TaigaMinClient( url=self.API_URL , token=self.API_TKN )
         
        response1 = tmc.rq('projects?is_backlog_activated=true&is_kanban_activated=true')
        if 200 != response1.status_code:
            print( response1.headers )
            print( response1 )
            self.fail( "Coudn't test projects/id/stats because the request for project list failed." )
            return
        lst = response1.json()
        print( str(len(lst)) + ' projects found.' )
        print( response1.headers )
        print( lst )
        return
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

