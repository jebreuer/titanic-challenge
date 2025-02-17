# Get the token with verbose output
echo "Requesting token..."
TOKEN_RESPONSE=$(curl -v -k -X 'POST' \
  'https://localhost:8443/auth/token?username=analyst&password=demo123' \
  -H 'accept: application/json' \
  -d '' 2>&1)

echo "Raw token response:"
echo "$TOKEN_RESPONSE"

# Extract token from response
TOKEN=$(echo "$TOKEN_RESPONSE" | grep "access_token" | jq -r .access_token)

# Verify we got a token
if [ -z "$TOKEN" ]; then
    echo "Failed to get token"
    exit 1
fi

echo "Token received: ${TOKEN:0:20}..."

# Make the schema request with proper Bearer format
curl -v -k "https://localhost:8443/schema" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
