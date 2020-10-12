#!/bin/bash -e

echo -e "curl -s http://localhost:8888/api/echo?abc=123"
curl -s "http://localhost:8888/api/echo?abc=123" --fail

echo -e "\ncurl -s http://localhost:8888/api/echo/echo?abc=123"
curl -s "http://localhost:8888/api/echo/echo?abc=123" --fail

echo -e "\ncurl -sXPOST http://localhost:8888/api/echo/echo -d @example-data.json"
curl -sXPOST "http://localhost:8888/api/echo/echo" -d @example-data.json --fail

echo -e "\ncurl -sXPOST http://localhost:8888/api/echo/echo -d @example-data.extended-json"
curl -sXPOST "http://localhost:8888/api/echo/echo" -d @example-data.extended-json --fail

echo -e ""

