#!/usr/bin/env bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
STOW_ARGS="-R --adopt --no-folding"
DEBUG=false

# Define packages to install
# Format: "package:target" or just "package" for $HOME
PACKAGES=(
    ".config:$HOME/.config"
    # "bin:$HOME/.local/bin"
)

# Logging
log() { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
debug() { [[ "$DEBUG" == true ]] && echo -e "${YELLOW}[DEBUG]${NC} $*"; }

# Help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
  --debug      Enable debug output
  --dry-run    Show what would be done
  --help, -h   Show this help

Uses GNU Stow with --no-folding to create file-level symlinks.
EOF
}

# Check dependencies
check_stow() {
    if ! command -v stow >/dev/null 2>&1; then
        error "GNU Stow not found. Install with: sudo apt install stow"
        exit 1
    fi
    debug "Using: $(stow --version | head -n1)"
}

# Parse package info
get_package() { echo "${1%%:*}"; }
get_target() {
    if [[ "$1" == *":"* ]]; then
        echo "${1#*:}"
    else
        echo "$HOME"
    fi
}

# Check if sudo needed
needs_sudo() { [[ "$1" != "$HOME"* ]] && [[ ! -w "$1" ]] 2>/dev/null; }

# Install package
install_package() {
    local pkg_info="$1"
    local package=$(get_package "$pkg_info")
    local target=$(get_target "$pkg_info")
    local sudo_cmd=""

    # Check if package exists
    if [[ ! -d "$package" ]]; then
        error "Package not found: $package"
        return 1
    fi

    # Check sudo requirement
    if needs_sudo "$target"; then
        sudo_cmd="sudo"
        log "Installing $package → $target (sudo required)"
    else
        log "Installing $package → $target"
    fi

    # Create target if needed
    [[ ! -d "$target" ]] && $sudo_cmd mkdir -p "$target"

    # Run stow
    debug "Command: $sudo_cmd stow --target=\"$target\" $STOW_ARGS \"$package\""

    if $sudo_cmd stow --target="$target" $STOW_ARGS "$package"; then
        success "Installed $package"
        return 0
    else
        error "Failed to install $package"
        return 1
    fi
}

# Dry run
dry_run() {
    log "=== DRY RUN ==="
    for pkg_info in "${PACKAGES[@]}"; do
        local package=$(get_package "$pkg_info")
        local target=$(get_target "$pkg_info")

        if [[ ! -d "$package" ]]; then
            error "Package not found: $package"
            continue
        fi

        log "Would install: $package → $target"
        if needs_sudo "$target"; then
            log "  (requires sudo)"
        fi

        debug "Files to link:"
        find "$package" -type f | head -5 | sed 's/^/  /'
        local count=$(find "$package" -type f | wc -l)
        [[ $count -gt 5 ]] && log "  ... and $((count - 5)) more files"
    done
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug) DEBUG=true; shift ;;
        --dry-run) dry_run; exit 0 ;;
        --help|-h) show_help; exit 0 ;;
        *) error "Unknown option: $1"; exit 1 ;;
    esac
done

# Main
main() {
    log "Dotfiles: $(pwd)"
    log "Packages: ${PACKAGES[*]}"

    check_stow

    local failed=0 success_count=0

    for pkg_info in "${PACKAGES[@]}"; do
        if install_package "$pkg_info"; then
            ((success_count++))
        else
            ((failed++))
        fi
    done

    echo
    if [[ $failed -eq 0 ]]; then
        success "All $success_count packages installed!"
    else
        error "$failed failed, $success_count succeeded"
        exit 1
    fi
}

main
