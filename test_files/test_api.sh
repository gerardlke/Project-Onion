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

echo "Pausing for 3 minutes to allow relationship pipeline to run...\n"
sleep 3m

echo "[API] GET /universe/relations"
curl -X GET $BASE_URL/universe/relations -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "[API] GET /universe/relation/{id}"
curl -X GET $BASE_URL/universe/relation/1 -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "===== 4. CHATBOT API ======"

# Single-turn query — no conversation history
echo "[API] POST /chat/query - single turn"
CHAT_RESPONSE=$(curl -s -X POST $BASE_URL/chat/query \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is a Binary Search Tree?",
       "conversation_history": []
     }')
echo "$CHAT_RESPONSE"
echo -e "\n"

# Validate that the response has the expected fields
CHAT_RESPONSE_TEXT=$(echo "$CHAT_RESPONSE" | sed -n 's|.*"response":"\([^"]*\)".*|\1|p')
if [ -z "$CHAT_RESPONSE_TEXT" ]; then
    echo "WARN: chat response field missing or empty"
else
    echo "PASS: chat response received"
fi

SOURCE_CONCEPTS=$(echo "$CHAT_RESPONSE" | grep -o '"source_concepts":\[.*\]')
if [ -z "$SOURCE_CONCEPTS" ]; then
    echo "WARN: source_concepts field missing — no relevant concepts retrieved or field absent"
else
    echo "PASS: source_concepts present — $SOURCE_CONCEPTS"
fi
echo -e "\n"

# Multi-turn query — passes prior turn as conversation history
# Tests that the backend correctly accepts and uses history without storing it server-side
echo "[API] POST /chat/query - multi-turn (with conversation history)"
curl -X POST $BASE_URL/chat/query \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "How does it differ from an AVL Tree?",
       "conversation_history": [
         {"role": "user",      "content": "What is a Binary Search Tree?"},
         {"role": "assistant", "content": "'"$CHAT_RESPONSE_TEXT"'"}
       ]
     }'
echo -e "\n"

# Query outside the uploaded knowledge base — tests graceful handling
# when no relevant concepts are found above the similarity threshold
echo "[API] POST /chat/query - out of domain query"
curl -X POST $BASE_URL/chat/query \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is the capital of France?",
       "conversation_history": []
     }'
echo -e "\n"

# Unauthenticated request — should return 401
echo "[API] POST /chat/query - unauthenticated (expect 401)"
curl -s -o /dev/null -w "HTTP status: %{http_code}\n" \
     -X POST $BASE_URL/chat/query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is recursion?",
       "conversation_history": []
     }'
echo -e "\n"

# Empty query — tests input validation
echo "[API] POST /chat/query - empty query (expect 422)"
curl -s -o /dev/null -w "HTTP status: %{http_code}\n" \
     -X POST $BASE_URL/chat/query \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "",
       "conversation_history": []
     }'
echo -e "\n"

echo "--- Testing Complete ---"