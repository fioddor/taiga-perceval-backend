#!/bin/bash
# Purpose: Smoke test: Access Taiga.io API.
# Design.: Needs jq installed.
#          See https://taigaio.github.io/taiga-doc/dist/api.html
# --------------------------------------------------------------------

SERVER=https://api.taiga.io/api/v1

# Request username and password for connecting to Taiga
read -p "Username or email: " USERNAME
read -r -s -p "Password: " PASSWORD


DATA=$(jq --null-input               \
	  --arg username "$USERNAME" \
	  --arg password "$PASSWORD" \
        '{ type: "normal", username: $username, password: $password }')

# Get AUTH_TOKEN
USER_AUTH_DETAIL=$( curl -X POST \
	            -H "Content-Type: application/json" \
	            -d "$DATA" \
	            https://api.taiga.io/api/v1/auth 2>/dev/null )

AUTH_TOKEN=$( echo ${USER_AUTH_DETAIL} | jq -r '.auth_token' )

# Exit if AUTH_TOKEN is not available
if [ -z ${AUTH_TOKEN} ]
then
    echo "Error: Incorrect username and/or password supplied"
    exit 1
else
    echo "auth_token is ${AUTH_TOKEN}"
fi




# Proceed to use API calls as desired
echo /---- RQ#1 pjs:
curl -iX GET                                  \
     -H "Content-Type: application/json"      \
     -H "Authorization: Bearer ${AUTH_TOKEN}" \
     -s $SERVER/projects > last.lstPjs.taiga.RS
echo \\

echo /--- RQ#2 pjs?page=2:
curl -iX GET                                  \
     -H "Content-Type: application/json"      \
     -H "Authorization: Bearer ${AUTH_TOKEN}" \
     -s $SERVER/projects?page=2 > last.lstPjs-p02.taiga.RS
echo \\

echo /--- RQ#3 pjs?page=3:
curl -iX GET                                  \
     -H "Content-Type: application/json"      \
     -H "Authorization: Bearer ${AUTH_TOKEN}" \
     -s $SERVER/projects?page=3 > last.lstPjs-P03.taiga.RS
echo \\

echo ---- FINISHED!
