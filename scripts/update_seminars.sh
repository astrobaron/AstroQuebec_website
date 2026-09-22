#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[seminars] refreshing from the two seminar sources..."
python3 scripts/import_seminars.py \
  --url "https://docs.google.com/spreadsheets/d/1ZFOU0qNz010exBnI2UC_IALXu3Kdp9gDFC_SuSLUScs/export?format=csv&gid=0" \
  --url "https://udemontreal-my.sharepoint.com/:x:/g/personal/david_lafreniere_umontreal_ca/IQDF7eQ5xo_uR4oiO99xV0NuAW1wxSKhLMBEbsuuyIx337I?e=qFSnfL"

echo "[seminars] rebuilding site..."
hugo --quiet
