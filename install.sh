#!/bin/bash

echo "▶️  Checking for 'stow'..."
if ! command -v stow &> /dev/null; then
    echo "❌ Error: 'stow' is not installed. Please install it to continue."
    echo "    - Debian/Ubuntu: sudo apt install stow"
    echo "    - Arch Linux: sudo pacman -S stow"
    echo "    - macOS (Homebrew): brew install stow"
    exit 1 # Exit with an error code
fi
echo "✅ 'stow' is installed."
echo ""

echo "▶️  Applying all dotfiles using 'stow'..."

# The -R (restow) flag first unstows and then stows again.
# This is useful for cleaning up old links and applying updates.
stow -R .

if [ $? -eq 0 ]; then
    echo "✅ Done! Symlinks were created successfully."
else
    echo "❌ Error: The 'stow' command failed."
    echo "   This is likely due to conflicting files in your home directory."
    echo "   How to fix:"
    echo "   1. Manually remove or back up the conflicting files (e.g., 'mv ~/.bashrc ~/.bashrc.bak') and run the script again."
    echo "   2. Alternatively, run 'stow --adopt .' in your terminal. This will move your existing files into this dotfiles repository."
fi
