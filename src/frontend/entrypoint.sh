#!/bin/sh
# Substitute BACKEND_URL and BACKEND_HOST into the nginx config template
# at runtime. Falls back to http://localhost:8000 for local Docker usage.
export BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
# Extract hostname from BACKEND_URL for SNI and Host header
export BACKEND_HOST=$(echo "$BACKEND_URL" | sed -E 's|https?://([^/:]+).*|\1|')
envsubst '${BACKEND_URL} ${BACKEND_HOST}' < /etc/nginx/conf.d/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
