#!/bin/bash

# Determine the root dir of the project
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Go to project cwd
cd "$PROJECT_DIR" || exit 1

# Load env from local .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

exec python3 main.py "$@"