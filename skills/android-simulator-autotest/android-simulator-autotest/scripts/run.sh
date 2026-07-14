#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(pwd)}"
"$SCRIPT_DIR/android_autotest.sh" "$ROOT_DIR"
