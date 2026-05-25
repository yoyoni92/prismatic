#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
docker compose --env-file ../.env up -d n8n runners
