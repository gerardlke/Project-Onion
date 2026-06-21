#!/bin/bash

clear

BASE_URL="http://localhost:8000"

echo "===== 1. USER AUTHENTICATION ====="
echo "[API] POST /user/create"
curl -X POST $BASE_URL/user/create -H "Content-Type: application/json" -d '{"username": "gerardlke", "password": "admin"}'
echo -e "\n"

echo "[API] POST /user/login"
TOKEN_RESPONSE=$(curl -s -X POST $BASE_URL/user/login -H "Content-Type: application/json" -d '{"username": "gerardlke", "password": "admin"}')
TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's|.*"access_token":"\([^"]*\)".*|\1|p')

if [ -z "$TOKEN" ]; then
    echo "Login failed or token not found. Exiting."
    exit 1
fi
echo "Successfully logged in and captured token."
echo -e "\n"


echo "===== 2. DOCUMENT UPLOAD ====="
echo "[API] POST /upload/new_topic"
curl -X POST $BASE_URL/upload/new_topic \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "CS1101s", "description": "Programming Methodology 1"}'
echo -e "\n"

echo "[API] GET /upload/get_topics"
curl -X GET $BASE_URL/upload/get_topics -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "[API] POST /upload/new_document - small notes"
curl -X POST $BASE_URL/upload/new_document \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@test_files/notes_small.txt" \
     -F "topic_name=CS1101s"
echo -e "\n"

echo "[API] POST /upload/new_document - big notes"
curl -X POST $BASE_URL/upload/new_document \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@test_files/note_big.txt" \
     -F "topic_name=CS1101s"
echo -e "\n"

echo "===== 3. UNIVERSE API ====="
echo "[API] GET /universe/topics"
curl -X GET $BASE_URL/universe/topics -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "[API] GET /universe/nodes"
curl -X GET "$BASE_URL/universe/nodes?dimensions=3" -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "[API] GET /universe/node/{id}"
curl -X GET $BASE_URL/universe/node/1 -H "Authorization: Bearer $TOKEN"
echo -e "\n"

# echo "[API] GET /universe/relations"
# curl -X GET $BASE_URL/universe/relations -H "Authorization: Bearer $TOKEN"
# echo -e "\n"

# echo "[API] GET /universe/relation/{id}"
# curl -X GET $BASE_URL/universe/relation/456 -H "Authorization: Bearer $TOKEN"
# echo -e "\n"

# echo "--- Testing Complete ---"