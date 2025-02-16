# Get the token
TOKEN=$(curl -X 'POST' \
  'http://localhost:8080/auth/token?username=analyst&password=demo123' \
  -H 'accept: application/json' \
  -d '' | jq -r .access_token)

# Verify we got a token
if [ -z "$TOKEN" ]; then
    echo "Failed to get token"
    exit 1
fi

# Make the schema request with proper Bearer format
curl -v "http://localhost:8080/schema" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
