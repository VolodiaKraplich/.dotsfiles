#!/bin/bash

# Check if the OS is Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Get the user's home directory
  HOME_DIR="$HOME"

  # Check if the .config directory exists in the current directory
  if [ -d ".config" ]; then
    # Copy the .config directory to the user's home directory
    cp -r .config "$HOME_DIR"
    echo ".config directory copied to $HOME_DIR"
  else
    echo ".config directory not found in the current directory"
  fi
else
  echo "This script is intended for Linux systems."
fi

exit 0
