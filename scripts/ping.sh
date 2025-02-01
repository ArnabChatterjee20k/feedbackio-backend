#!/bin/bash

URL=$PROD_URL
STATUS_CODE=$(curl -o /dev/null -s -w "%{http_code}" -I "$URL")

echo "Status Code: $STATUS_CODE"

if [[ "$STATUS_CODE" -ne 200 ]]; then
    echo "⚠️ Warning: $URL is not responding with 200 OK"
    exit 1
fi

exit 0