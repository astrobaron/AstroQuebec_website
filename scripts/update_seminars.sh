#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[seminars] refreshing from Google Sheet..."
python3 scripts/import_seminars.py --url "https://docs.google.com/spreadsheets/d/1ZFOU0qNz010exBnI2UC_IALXu3Kdp9gDFC_SuSLUScs/export?format=csv&gid=0"

echo "[seminars] rebuilding site..."
hugo --quiet
