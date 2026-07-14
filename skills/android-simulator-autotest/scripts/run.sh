#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -lt 1 ]]; then
  echo "ERROR: missing project root argument."
  echo "Usage: $0 /absolute/path/to/project"
  exit 2
fi
ROOT_DIR="$1"
"$SCRIPT_DIR/android_autotest.sh" "$ROOT_DIR"
