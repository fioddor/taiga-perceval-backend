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
# Purpose: Minimalistic smoke test.
#
# Design.: + Script structure.
#          + Manual validation.
#
# Author.: Fioddor Superconcentrado <fioddor@gmail.com>
#
#-----------------------------------------------------------------------------------------------------------------------------------------

import sys , requests        



H_CT   = {'Content-Type': 'application/json'}
SERVER = 'https://api.taiga.io/api/v1/'


if 3 != len(sys.argv):
    print( 'Required 2 args: user and pass. {} arguments passed.'.format(len(sys.argv)-1) )
else:
    print( sys.argv[1] + ':' + sys.argv[2] )

data_str = '{ ' + '"type": "normal", "username": "{}", "password": "{}"'.format( sys.argv[1] , sys.argv[2] ) + ' }'
data_ba  = bytearray(data_str, encoding='utf-8')
print(data_ba)


rs0 = requests.post( SERVER+'auth',data=data_ba, headers=H_CT)

if 200==rs0.status_code:
    S_HEADERS = H_CT
    S_HEADERS['Authorization'] = 'Bearer ' + rs0.json()['auth_token']
    print(S_HEADERS)
    
    rs1 = requests.get( SERVER+'projects' , headers=S_HEADERS)

    print('/--- Rq#1: /projects:')
    print(rs1.headers)
    print(rs1.request.body)
    print(rs1.status_code)
    print(rs1.text)
    print('\n---')
    lst = rs1.json()
    print(len(lst))

    print('\\--- Rq#1.')

else:
    print(rs0.request.body)
    print(rs0.status_code)
    print(rs0.text)

