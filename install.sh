#!/bin/bash
set -e
set -u # Exit on unset variables

# Constants
SCRIPT_NAME=$(basename "$0")

# Global variables
NO_SYS=false
DISTRO_ID=""
DISTRO_LIKE=""
PYTHON_BIN=""

# Log message function
log() {
  echo "[$SCRIPT_NAME] $1"
}

# Error message function
error() {
  echo "[$SCRIPT_NAME] ERROR: $1" >&2
  exit 1
}

# Parse command line arguments early for --no-sys
parse_arguments() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --no-sys)
        NO_SYS=true
        ;;
      # Other arguments will be passed to install.py
      *)
        ;;
    esac
    shift
  done
}

# Detect Linux distribution
detect_distribution() {
  if [ ! -f /etc/os-release ]; then
    error "Cannot determine Linux distribution"
  fi

  . /etc/os-release
  DISTRO_ID=$(echo "${ID,,}" | tr -d '[:space:]')
  DISTRO_LIKE=$(echo "${ID_LIKE,,}" | tr -d '[:space:]')

  log "Detected distribution: ${NAME:-Unknown}"
}

# Install Python based on distribution
install_python() {
  local distro="$1"
  case "$distro" in
    debian|ubuntu|linuxmint)
      sudo apt update && sudo apt install -y python3
      ;;
    fedora|nobara)
      sudo dnf install -y python3
      ;;
    opensuse*|suse)
      sudo zypper install -y python3
      ;;
    arch|manjaro|endeavouros)
      sudo pacman -Sy --noconfirm python
      ;;
    *)
      return 1
      ;;
  esac
}

# Check and install Python if needed
setup_python() {
  if command -v python3 &>/dev/null; then
    PYTHON_BIN=$(command -v python3)
  elif command -v python &>/dev/null; then
    PYTHON_BIN=$(command -v python)
  else
    log "Python is not installed."
    read -p "Do you want to install Python now? [Y/n]: " INSTALL_PY
    INSTALL_PY=${INSTALL_PY:-Y}

    if [[ "$INSTALL_PY" =~ ^[Yy]$ ]]; then
      local distro_to_install="unknown"
      local installed=false

      # Determine distribution type
      for distro in "$DISTRO_ID" "$DISTRO_LIKE"; do
        if [ -n "$distro" ]; then
          for known_distro in debian fedora opensuse arch; do
            if [[ "$distro" == *"$known_distro"* ]]; then
              distro_to_install="$known_distro"
              if install_python "$distro_to_install"; then
                PYTHON_BIN=$(command -v python3 || command -v python)
                if [ -n "$PYTHON_BIN" ]; then
                  installed=true
                  break 3
                fi
              fi
            fi
          done
        fi
      done

      if [ "$installed" = false ]; then
          error "Automatic Python installation not supported for this distribution"
      fi
    else
      error "Python is required. Exiting."
    fi
  fi

  if [ -z "$PYTHON_BIN" ]; then
      error "Python binary not found after installation attempt."
  fi

  log "Python found: $($PYTHON_BIN --version 2>&1)"
}

# Main execution
main() {
  # Check OS
  if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    error "This script is intended for Linux systems"
  fi

  # Parse arguments to potentially set --no-sys early
  parse_arguments "$@"

  # Detect distribution
  detect_distribution

  # Special case: CachyOS
  if [[ "$DISTRO_ID" == "cachyos" ]]; then
    NO_SYS=true
    log "Detected CachyOS. Automatically skipping system files installation"
  fi

  # Setup Python
  setup_python

  # Set environment variables for the Python script
  export DOTFILES_INSTALLATION=true
  export PYTHON_BIN="$PYTHON_BIN"
  export NO_SYS="$NO_SYS" # Pass no_sys state to python script

  # Run the installation script
  log "Starting dotfiles installation using Python..."
  "$PYTHON_BIN" install.py "$@"
}

main "$@"
