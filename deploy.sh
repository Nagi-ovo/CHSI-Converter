#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
release="${CHSI_RELEASE:-$(git rev-parse --short HEAD)}"
port="${CHSI_PORT:-8002}"
if ! docker info --format '{{json .SecurityOptions}}' | grep -q rootless; then
  echo "Use the dedicated user's rootless Docker context." >&2
  exit 1
fi
if ss -ltn "sport = :$port" | grep -q LISTEN; then
  echo "Port $port is occupied. Stage the new release on an unused localhost port." >&2
  exit 1
fi
export CHSI_RELEASE="$release" CHSI_PORT="$port"
docker compose -p "chsi-$release" build \
  --build-arg "PYPI_INDEX_URL=${PYPI_INDEX_URL:-https://pypi.org/simple}" \
  --build-arg "DEBIAN_MIRROR=${DEBIAN_MIRROR:-deb.debian.org}"
docker compose -p "chsi-$release" up -d --wait --wait-timeout 60
curl --fail --silent --show-error "http://127.0.0.1:$port/healthz"
echo
echo "Release $release is staged on localhost:$port. Verify conversion before switching Nginx."
