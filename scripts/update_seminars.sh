#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[seminars] refreshing from the two seminar sources..."
python3 scripts/import_seminars.py \
  --url "https://docs.google.com/spreadsheets/d/1ZFOU0qNz010exBnI2UC_IALXu3Kdp9gDFC_SuSLUScs/export?format=csv&gid=0" \
  --url "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQuijtqP317H2sYk84mriq9OTQhW624Jwn0RH5nv1OHdKsKTYggxKFnax9GAjG2dkT8OxH7825VrSW/pub?output=csv"

echo "[seminars] rebuilding site..."
hugo --quiet
