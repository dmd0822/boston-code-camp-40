#!/bin/sh
# Substitute BACKEND_URL into the nginx config template at runtime.
# Falls back to http://localhost:8000 for local Docker usage.
export BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
