#!/usr/bin/env bash

#
# Simple Stow Installation Script
#
# Automatically installs specified packages using GNU Stow
# Supports custom target directories including system paths
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
STOW_ARGS="-R --adopt"
STOW_DIR="$(pwd)"
HOME_DIR="$HOME"

# Define packages to install with their target directories
# Format: "package_name:target_directory" or just "package_name" for $HOME
PACKAGES=(
    ".config"
    # "etc:/etc"
    # "systemd:/etc/systemd"
    # "nginx:/etc/nginx"
)

# Logging functions
info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Check if stow is installed
check_stow() {
    if ! command -v stow &> /dev/null; then
        error "GNU Stow is not installed!"
        info "Install with: sudo apt install stow  (or  brew install stow)"
        exit 1
    fi
}

# Get package name from package info
get_package_name() {
    local package_info="$1"
    echo "${package_info%%:*}"
}

# Get target directory for package
get_target() {
    local package_info="$1"

    if [[ "$package_info" == *":"* ]]; then
        echo "${package_info#*:}"
    else
        echo "$HOME_DIR"
    fi
}

# Check if target requires sudo
needs_sudo() {
    local target="$1"

    if [[ "$target" != "$HOME_DIR"* ]] && [[ ! -w "$target" ]] 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Install single package
install_package() {
    local package_info="$1"
    local package target sudo_cmd=""

    package=$(get_package_name "$package_info")
    target=$(get_target "$package_info")

    if needs_sudo "$target"; then
        sudo_cmd="sudo"
        info "Installing $package → $target (requires sudo)"
    else
        info "Installing $package → $target"
    fi

    if [[ ! -d "$target" ]]; then
        if [[ -n "$sudo_cmd" ]]; then
            sudo mkdir -p "$target"
        else
            mkdir -p "$target"
        fi
    fi

    if $sudo_cmd stow --dir="$STOW_DIR" --target="$target" $STOW_ARGS "$package" 2>/dev/null; then
        success "Installed $package"
        return 0
    else
        error "Failed to install $package"
        return 1
    fi
}

# Main function
main() {
    local failed=0
    local success_count=0
    local package

    info "Stow directory: $STOW_DIR"
    info "Packages: ${PACKAGES[*]}"

    check_stow
    echo

    for package_info in "${PACKAGES[@]}"; do
        package=$(get_package_name "$package_info")

        if [[ ! -d "$STOW_DIR/$package" ]]; then
            error "Package directory not found: $package"
            ((failed++))
            continue
        fi

        if install_package "$package_info"; then
            ((success_count++))
        else
            ((failed++))
        fi
    done

    echo
    if [[ $failed -eq 0 ]]; then
        success "All $success_count packages installed successfully!"
    else
        error "$failed packages failed, $success_count succeeded"
        exit 1
    fi
}

main "$@"
