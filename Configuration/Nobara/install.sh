#!/bin/bash

# Ensure Python can import Configuration as a package
export PYTHONPATH="$(pwd)/../.."

# Functions for logging messages
log_info() {
    echo "INFO: $1"
}

log_warn() {
    echo "WARN: $1"
}

log_error() {
    echo "ERROR: $1" >&2
}

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Check if the OS is Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
  log_error "This script is intended for Linux systems only."
  exit 1
fi
log_info "OS check passed: This is a Linux system."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    log_warn "Python 3 is not found."
    read -r -p "Python 3 is required to run these configuration scripts. Do you want to install it? (yes/no): " install_python_confirm

    if [[ "$install_python_confirm" =~ ^[Yy][Ee]?[Ss]?$ ]]; then
        log_info "Attempting to install Python 3 using dnf..."
        # Assuming dnf is the package manager (common on Nobara/Fedora)
        if sudo dnf install -y python3; then
            log_info "Python 3 installed successfully."
        else
            log_error "Failed to install Python 3. Please install it manually and re-run the script."
            exit 1
        fi
    else
        log_error "Python 3 installation declined. Cannot proceed without Python 3."
        exit 1
    fi
fi

log_info "Python 3 is installed. Proceeding with configuration scripts."

# Function to execute Python scripts in a directory
execute_python_scripts() {
    local dir="$1"
    log_info "Executing Python scripts in directory: $dir"
    find "$dir" -name "*.py" -print0 | sort -z | while IFS= read -r -d $'\0' script; do
        # Skip __init__.py files
        if [[ "$(basename "$script")" == "__init__.py" ]]; then
            continue
        fi
        log_info "Executing script: $script"
        # Pass SUDO_USER_HOME to Python scripts if running under sudo
        if [[ -n "$SUDO_USER" ]]; then
            SUDO_USER_HOME=$(eval echo "~$SUDO_USER")
            export SUDO_USER_HOME
        fi
        # Запускати як модуль, щоб працювали імпорти (потрібно запускати з кореня Linux-Tweaks)
        rel_path="${script#$SCRIPT_DIR/}"
        module_path="Configuration.Nobara.${rel_path%.py}"
        module_path="${module_path//\//.}"
        if ! python3 -m "$module_path"; then
            log_error "Failed to execute script: $script"
            return 1
        fi
    done
    return 0
}


# 1. Execute scripts in the 'repos' directory
if ! execute_python_scripts "repos"; then
    log_error "Failed to execute scripts in 'repos' directory. Exiting."
    exit 1
fi

# 2. Execute 'cleanup.py' as a module
log_info "Executing cleanup.py"
if [[ -n "$SUDO_USER" ]]; then
    SUDO_USER_HOME=$(eval echo "~$SUDO_USER")
    export SUDO_USER_HOME
fi
if ! python3 -m Configuration.Nobara.cleanup; then
    log_error "Failed to execute cleanup.py. Exiting."
    exit 1
fi

# 3. Execute scripts in the 'pkgs' directory
if ! execute_python_scripts "pkgs"; then
    log_error "Failed to execute scripts in 'pkgs' directory. Exiting."
    exit 1
fi

# 4. Execute scripts in the 'patches' directory
if ! execute_python_scripts "patches"; then
    log_error "Failed to execute scripts in 'patches' directory. Exiting."
    exit 1
fi

log_info "Nobara configuration completed successfully."

exit 0
