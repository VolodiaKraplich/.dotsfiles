# Configuration Scripts for My Dots!

A comprehensive dotfiles repository designed to automate the setup and configuration of Linux systems. This repository includes Python scripts, shell configurations, and system settings that handle package management, repository configuration, system cleanup, and user-specific customizations.

## 🌟 Key Features

- **Fish Shell Configuration**
  - Custom prompt with git integration
  - Enhanced command-line utilities and aliases
  - Modern command replacements (eza, bat)
  - Command completion notifications
  - Git workflow helper functions

- **Development Tools**
  - Git configuration with sensible defaults
  - Global gitignore patterns
  - Code editor settings (Zed)

- **System Configuration**
  - AMD GPU optimizations
  - ZRAM configuration
  - Efficient backup mechanism

- **Terminal Customization**
  - Ghostty terminal configuration with Catppuccin theme
  - Cascadia Code font
  - Custom command not found handler

## 📁 Directory Structure

```
Configuration/
├── system/              # System-wide configurations
│   ├── etc/amdgpu.conf
│   └── etc/systemd/zram-generator.conf
└── user/               # User-specific configurations
    ├── .config/
    │   ├── fastfetch/  # System information display
    │   ├── fish/       # Fish shell configuration
    │   ├── ghostty/    # Terminal emulator settings
    │   └── git/        # Git configuration
    └── patches/        # System patches
```

## 🚀 Installation

1. Clone the repository:
   ```
   git clone https://github.com/v1mkss/.dotsfiles.git --depth=1
   cd .dotsfiles
   ```

2. Run the installation script:
   ```
   ./install.sh
   ```

### Installation Options

- `--no-bak`: Skip backup creation of existing files
- `--no-sys`: Skip system file installations

## 🛠 Shell Features

### Fish Shell Enhancements

- **Modern Command Replacements**
  - `ls` → `eza` with icons and colors
  - `cat` → `bat` with syntax highlighting
  - Enhanced directory navigation aliases

- **Git Workflow**
  - Streamlined git commands via `gf` function
  - Git branch information in prompt
  - Common git aliases

- **Utility Functions**
  - `mkcd`: Create and enter directory
  - `backup`: Quick file backup
  - Command completion notifications

### Terminal Configuration

- Ghostty terminal emulator
  - Catppuccin Mocha theme
  - Cascadia Code font family
  - KDE integration

## ⚙️ System Configurations

### AMD GPU Settings
- Force AMDGPU driver for GCN 1.0+ cards
- Rusticl support for Radeon SI

### ZRAM Configuration
- 12GB ZRAM size
- ZSTD compression
- Swap priority optimization

## 🔧 Development Setup

### Git Configuration
- Default branch: master
- Auto CRLF handling
- Rebase on pull
- Auto remote setup
- Custom color scheme

### Global Git Ignore
- Editor files (.idea, .vscode, .zed)
- Build outputs
- Dependencies
- Environment files
- Logs and caches

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests for any improvements or bug fixes.

## 📝 License

This project is licensed under the MIT License.

## 🔍 Notes

- The installation script automatically detects your Linux distribution and installs required dependencies
- System configurations are backed up with `.bak` suffix before modification
- Fish shell configurations require Fish 4.0 or newer
- Some features require additional packages (eza, bat, git)
