#!/bin/bash

# Determine the root dir of the project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Go to project root
cd "$PROJECT_ROOT" || exit 1

if [ -z "$1" ]; then
    echo "Error: environment file name not set."
    echo "Usage: $0 <path_to_env_file>"
    exit 1
fi

ENV_FILE="$1"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Error: environment file '$ENV_FILE' not found."
    exit 1
fi

python3 main.py