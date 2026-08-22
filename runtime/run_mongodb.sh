#!/usr/bin/env bash
set -euo pipefail

readonly IMAGE='mongo@sha256:d7c8d78b890e2d87ff11b30656a6c991addcc260723c9be723123041763d00a8'

docker volume create resolve-mongo-data >/dev/null
exec docker run \
  --name resolve-mongodb \
  --pull=never \
  --restart unless-stopped \
  -p 127.0.0.1:27017:27017 \
  -v resolve-mongo-data:/data/db \
  "${IMAGE}"
