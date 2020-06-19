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
# Usage..: Instantiate object from other python program.
# Author.: Fioddor Superconcentrado <fioddor@gmail.com>
#
#----------------------------------------------------------------------------------------------------------------------

import requests
import time
from math import ceil

import logging
logging.basicConfig( level=logging.INFO ) #DEBUG )
logger = logging.getLogger(__name__)



class TaigaMinClient(): #HttpClient):

    '''Minimalistic Taiga Client.
    
    Usage..: 1. Instantiate object from other python program with either
                a) API token or
                b) user and password
             2. Only if you instantiated with user and password (b) you need to (call) login.
    
    Design.: - Asynchronous =>
               - Close client sessions (pass them closed).
               - Signal server to close HTTP session.
                 See https://stackoverflow.com/questions/10115126/python-requests-close-http-connection#15511852
    
    Pending: - We don't yet see a compelling reason to implement application-token authentication.
             - In our reference Taiga instance (taiga.io) project export needs special permissions we don't have.
    '''
    
    VERSION = '20200619A' 
    
    ME = 'TaigaMinClient-{}'.format( VERSION )
    H_STANDARD_BASE = { 'Content-Type': 'application/json'
                      ,   'Connection': 'close'
                      }
    
    token   = None
    
    
    def censor(self, uncensored ):
        '''Returns a censored version of the given text.'''
        length    = len(uncensored)
        verbosity = 3 if 8 < length else 1
        return '{}...{}'.format( uncensored[0:verbosity] , uncensored[-verbosity:] )
    
    
    def __set_headers__(self):
        '''(Re)sets session headers according to current client property values.'''
        
        self.headers = self.H_STANDARD_BASE.copy()
        self.headers['Authorization'] = 'Bearer ' + self.token
        
        logger.debug( self.ME+'.set_headers as ' + str(self.headers) )
    
    
    def __init__(self
                , url=None, ssl_verify=True
                , user=None, pswd=None, token=None
                , sleep_time=1, max_retries=5
                , extra_retry_after_status=[500 , 502]
                , archive=False, from_archive=None
                ):
        '''Init client.
        
        :param:   url: url of the Taiga instance. Mandatory.
        :param: token: API token for client authentication.
        :param:  user: API user to be used along with pswd to get a token.
        :param:  pswd: API pswd to be used along with user to get a token.
        If all optional parameters are missing raises Exception.
        If all optional parameters are provided token is taken while user and pswd
        are ignored.

        Pending: - headers
                 - ssl_verify
                 - throttling
                 - archive
        '''
        
        ME = self.ME + '.__init__'
        
        if not url:
            raise Missing_Init_Arguments( 'url (Taiga API base URL).')
        self.base_url = url
        
        if token:
            self.token = token
            self.__set_headers__()
            logger.debug( ME+'( ' + self.censor(self.token) + ' ).' ) 
        elif user and pswd:
            self.user = user
            self.pswd = pswd
            logger.debug( '{} {}:{}@{}'.format(ME , self.user , self.censor(self.pswd) , self.base_url) )
        else:
            raise Missing_Init_Arguments( 'either API token or Taiga user and pswd.' )
    
    
    def get_token(self):
        '''Returns session token for reuse.'''
        return self.token
     
     
    def login(self):
        '''Gets session token from API and (re)sets session headers accordingly.'''
        
        TEMPLATE = '"type": "normal", "username": "{}", "password": "{}"'
        
        try:
            data_str = '{ ' + TEMPLATE.format( self.user , self.pswd ) + ' }'
        except AttributeError:
            raise Login_Lacks_Credentials
        data_ba = bytearray( data_str , encoding='utf-8' )
        
        rs = requests.post( self.base_url+'auth' , data=data_ba , headers=self.H_STANDARD_BASE )
        rs.close()
        
        if 200 == rs.status_code:
            self.token = rs.json()['auth_token']
            self.__set_headers__()
        else:
            censored = str(rs.request.body).replace(self.pswd , self.censor(self.pswd))
            
            ME = self.ME + '.login'
            logger.error( ME + ' failed:'                                     )
            logger.error( ME + ' Rq.headers : '     + str(rs.request.headers) )
            logger.error( ME + ' Rq.body : '        + str(censored)           )
            logger.error( ME + ' Rs.status_code : ' + str(rs.status_code )    )
            logger.error( ME + ' Rs.text:\n'        + rs.text                 )
            raise Exception( ME + 'failed. Check the log!' )
    
    
    def __http_get__(self, url , caller ):
        '''Wrap the request debugging and failure handling.

        URLs are usually fed by users and tend to fail. It helps him a lot
        to report the actual URL called.
        Connection failures show quite some stacktrace. Marking the return
        of the control to this method also helps.
        
        :param: url: URL to retrieve.
        :param: caller: a string naming the caller point. Will be used in
                        the logger messages.
        :returns: an open requests response. The full object is returned
                  (whether successful or not) for further analysis. Only
                  raises an exception if the client is not initiated.
        '''
        me = self.ME + caller
        
        if not self.headers:
            raise Uninitiated_TaigaClient( '.{}({}).'.format( me , url) )
        
        logger.debug(  '/ {}({})'.format( me , url ) )
        
        response = requests.get( url , headers=self.headers )
        
        if 429 == response.status_code:
            words = response.json()['_error_message'].split()
            nums = [ int(w) for w in words if w.isdigit() ]
            if 1 == len(nums):
                delay = nums[0]
                logger.info( 'Sleeping for {} seconds...'.format( delay ) )
                time.sleep( delay )

                response = requests.get( url , headers=self.headers )
        
        logger.debug( '\\ {}({})'.format( me , url ) )
        
        return response
    
    
    def basic_rq(self, query):
        '''Most basic exposed request handler.
         
        :returns: a closed requests response. The full object is returned
                  (whether successful or not) for further analysis.
        '''
        api_command = self.base_url + query
        
        response = self.__http_get__( api_command , '.basic_rq.' )
        response.close()
        
        return response
     
     
    def rq(self, query, max_page=None):
        '''Generic request handler.
         
        :param max_page: maximum number of page to request. All pages, if this argument is missing.
        :returns: a list of Taiga JSON objects. Raises exceptions if anything fails.
        '''
        def get_page( url ):
            response = self.__http_get__( url , '.rq.get_page' )
            if 200 != response.status_code:
                raise Unexpected_HTTPcode( url , response )
            return response
        
        api_command = self.base_url + query
        
        response = get_page( api_command )
        output = response.json()
        
        if all(key in response.headers for key in ( 'x-paginated' , 'x-pagination-count' , 'x-paginated-by' )):
            max_taiga = ceil( int(response.headers['x-pagination-count'])
                            / int(response.headers['x-paginated-by'    ])
                            )
            if max_page:
                maximum = min([ max_page , max_taiga ])
            else:
                maximum = max_taiga
            
            while int(response.headers['x-pagination-current']) < maximum:
                next_url = response.headers['X-Pagination-Next']
                response = get_page( next_url )

                # print( response.headers )
                output.extend( response.json() )
                logger.info( self.ME+'.rp_pages got yet {} items out of {}.'.
                       format( len(output) , response.headers['x-pagination-count'] )
                     )
        
        response.close()
        return output
     
     
    def get_lst_data_from_api(self, query, key_list):
        '''Cherry-picks a given list of items from an endpoint.
         
        :param: key_list: a list of the JSON keys of all items to retrieve.
        :returns: a dictionary with all retrieved items. It raises Exceptions
            if any item is missing. 
        '''
        record = self.rq( query )
        output = {}
        for datum in key_list:
            if datum in record:
                output[ datum ] = record[ datum ]
            else:
                raise Missing_Expected_Item( datum , query )
        return output
    
    
    def proj_stats(self, project):
        '''Retrieve some basic stats from the given project.'''
         
        STATISTICS = ( 'total_milestones' , 'total_points' , 'closed_points' , 'defined_points' , 'assigned_points' )
        api_command = 'projects/{}/stats'.format( project )
         
        return self.get_lst_data_from_api( api_command , STATISTICS )
     
     
    def proj_issues_stats(self, project):
        '''Retrieve some basic issues_stats from the given project.'''
        
        STATISTICS = ( 'total_issues' , 'opened_issues' , 'closed_issues'
                     , 'issues_per_priority' , 'issues_per_severity' , 'issues_per_status'
                     )
        api_command = 'projects/{}/issues_stats'.format( project )
        
        return self.get_lst_data_from_api( api_command , STATISTICS )
    
    
    def proj(self, project):
        '''Retrieve all information about the given project.
        
        Since we're not allowed to export a project we request the data by parts.
        '''
        
        BLOCKS = ( (       'basics' , 'projects/{}'              )
                 , (        'stats' , 'projects/{}/stats'        )
                 , ( 'issues_stats' , 'projects/{}/issues_stats' )
                 , (        'epics' ,       'epics?project={}'   )
                 , (  'userstories' , 'userstories?project={}'   )
                 , (        'tasks' ,       'tasks?project={}'   )
                 , (         'wiki' ,        'wiki?project={}'   )
                 )
        project_info = {}
        
        for name , url in BLOCKS:
            project_info[name] = self.rq( url.format( project ) )
        
        return project_info



class Uninitiated_TaigaClient(Exception):
    '''An uninitiated TaigaCLient has been requested to do something only initiated ones can do.'''
    def __init__(self, details=''):
        ERR_MESSAGE = 'An uninitiated Taigaclient has been requested to do something only initiated ones can do.'
        if details:
            super().__init__( ERR_MESSAGE + ' ' + details )


class Missing_Init_Arguments(Exception):
    '''Missing arguments instantiating a TaigaCLient.'''
    def __init__(self, details):
        ERR_MESSAGE = 'Minimal arguments are missing instantiating a TaigaCLient:'
        ERR_MESSAGE += ' ' + details
        super().__init__( ERR_MESSAGE )


class Login_Lacks_Credentials(Exception):
    '''Login lacks user or pswd.'''
    def __init__(self, details=None):
        ERR_MESSAGE = 'Missing user or pswd at TaigaCLient.login. (Remember that token-born clients do not need to login!)'
        if details:
            ERR_MESSAGE += ' ' + details
        super().__init__( ERR_MESSAGE )


class Unexpected_HTTPcode(Exception):
    '''HTTP returned an unexpected code.'''
    def __init__(self, url, response , details=None):
        ERR_MESSAGE = 'Unexpected Http return code {} retrieving {}: {}'.format(response.status_code , url, response.text)
        if details:
            ERR_MESSAGE += ' ' + details
        super().__init__( ERR_MESSAGE )


class Missing_Expected_Item(Exception):
    '''An expected item is missing in a dataset.'''
    def __init__(self, datum , query , details=None):
        ERR_MESSAGE = 'Missing expected {} in {}'.format(datum , query)
        if details:
            ERR_MESSAGE += ' ' + details
        super().__init__( ERR_MESSAGE )
