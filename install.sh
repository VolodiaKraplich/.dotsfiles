#!/usr/bin/env bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
STOW_ARGS="-R --adopt"
STOW_DIR="$(pwd)"
HOME_DIR="$HOME"
DEBUG_MODE=false

# Define packages to install with their target directories
# Format: "package_name:target_directory" or just "package_name" for $HOME
PACKAGES=(
    ".config:$HOME/.config"
    # "etc:/etc"
    # "systemd:/etc/systemd"
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

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

debug() {
    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo -e "${YELLOW}[DEBUG]${NC} $*"
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --debug      Enable debug output"
    echo "  --dry-run    Show what would be done without making changes"
    echo "  --help, -h   Show this help message"
    echo
    echo "This script uses GNU Stow to manage dotfiles and configuration files."
}

# Check if stow is installed
check_stow() {
    if ! command -v stow &> /dev/null; then
        error "GNU Stow is not installed!"
        info "Install with: sudo apt install stow  (or  brew install stow)"
        exit 1
    fi
    debug "GNU Stow version: $(stow --version | head -n1)"
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

# Show package structure
show_package_structure() {
    local package="$1"
    debug "Package structure for $package:"
    if [[ -d "$STOW_DIR/$package" ]]; then
        find "$STOW_DIR/$package" -type f | head -10 | sed 's/^/  /'
        local file_count=$(find "$STOW_DIR/$package" -type f | wc -l)
        if [[ $file_count -gt 10 ]]; then
            echo "  ... and $((file_count - 10)) more files"
        fi
    fi
}

# Check for conflicts before stowing
check_conflicts() {
    local package="$1"
    local target="$2"
    local sudo_cmd="$3"

    debug "Checking for conflicts in $package → $target"

    local stow_output
    if stow_output=$($sudo_cmd stow --dir="$STOW_DIR" --target="$target" --no -v "$package" 2>&1); then
        debug "No conflicts detected for $package"
        return 0
    else
        warning "Potential conflicts detected for $package:"
        echo "$stow_output" | grep -E "(existing|conflict|WARNING)" || echo "$stow_output"
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

    # Show package structure
    show_package_structure "$package"

    # Create target directory if needed
    if [[ ! -d "$target" ]]; then
        debug "Creating target directory: $target"
        if [[ -n "$sudo_cmd" ]]; then
            sudo mkdir -p "$target"
        else
            mkdir -p "$target"
        fi
    fi

    # Check for conflicts first
    if ! check_conflicts "$package" "$target" "$sudo_cmd"; then
        warning "Conflicts detected. Proceeding with --adopt flag to resolve them."
    fi

    # Run stow with verbose output for debugging
    debug "Running: $sudo_cmd stow --dir=\"$STOW_DIR\" --target=\"$target\" $STOW_ARGS \"$package\""

    local stow_output
    if stow_output=$($sudo_cmd stow --dir="$STOW_DIR" --target="$target" $STOW_ARGS "$package" 2>&1); then
        success "Installed $package"
        debug "Stow output: $stow_output"
        return 0
    else
        error "Failed to install $package"
        error "Stow output: $stow_output"

        # Additional debugging information
        debug "Directory permissions:"
        ls -la "$STOW_DIR" | grep "$package" || echo "Package directory not found in listing"
        debug "Target directory permissions:"
        ls -la "$target" 2>/dev/null || echo "Target directory doesn't exist or not accessible"

        return 1
    fi
}

# Dry run function
dry_run() {
    info "=== DRY RUN MODE ==="
    for package_info in "${PACKAGES[@]}"; do
        local package target sudo_cmd=""
        package=$(get_package_name "$package_info")
        target=$(get_target "$package_info")

        if needs_sudo "$target"; then
            sudo_cmd="sudo"
        fi

        info "Would install: $package → $target $([ -n "$sudo_cmd" ] && echo "(with sudo)")"

        if [[ ! -d "$STOW_DIR/$package" ]]; then
            error "Package directory not found: $package"
            continue
        fi

        show_package_structure "$package"
        check_conflicts "$package" "$target" "$sudo_cmd"
        echo
    done
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug)
                DEBUG_MODE=true
                shift
                ;;
            --dry-run)
                dry_run
                exit 0
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Main function
main() {
    local failed=0
    local success_count=0

    # Parse command line arguments
    parse_args "$@"

    info "Stow directory: $STOW_DIR"
    info "Packages: ${PACKAGES[*]}"

    check_stow
    echo

    for package_info in "${PACKAGES[@]}"; do
        local package=$(get_package_name "$package_info")

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
        echo
    done

    echo
    if [[ $failed -eq 0 ]]; then
        success "All $success_count packages installed successfully!"
    else
        error "$failed packages failed, $success_count succeeded"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
