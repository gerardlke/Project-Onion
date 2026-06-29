#!/bin/bash

clear

BASE_URL="http://localhost:8000"

echo "[API] POST /user/login"
TOKEN_RESPONSE=$(curl -s -X POST $BASE_URL/user/login -H "Content-Type: application/json" -d '{"username": "gerardlke", "password": "admin"}')
TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's|.*"access_token":"\([^"]*\)".*|\1|p')

if [ -z "$TOKEN" ]; then
    echo "Login failed or token not found. Exiting."
    exit 1
fi
echo "Successfully logged in and captured token."
echo -e "\n"

echo "[API] GET /universe/topics"
curl -X GET $BASE_URL/universe/topics -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "[API] GET /universe/nodes"
curl -X GET "$BASE_URL/universe/nodes?dimensions=3" -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "--- Testing Complete ---"