# 🏠 Dotfiles

A clean and organized collection of configuration files for a modern development environment. Managed with GNU Stow for easy installation and maintenance.

## 🚀 Quick Start

### Prerequisites

- **GNU Stow** - Package manager for dotfiles

  ```bash
  # Ubuntu/Debian
  sudo apt install stow

  # macOS
  brew install stow

  # Arch Linux
  sudo pacman -S stow
  ```

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/VolodiaKraplich/dotfiles.git
   cd dotfiles
   ```

2. **Run the installer:**
   ```bash
   ./install.sh
   ```

That's it! The script will automatically:

- Install all configuration files to appropriate locations
- Handle existing files safely with `--adopt` flag
- Create necessary directories if they don't exist

### Reinstallation

To update or reinstall configurations:

```bash
./install.sh
```

The script uses stow's restow (`-R`) feature to cleanly reinstall configurations.

## 🔧 Troubleshooting

### Stow Conflicts

If you encounter stow conflicts:

```bash
# Remove existing symlinks
stow -D .config

# Reinstall
./install.sh
```

### Missing Fonts

Install required fonts:

- **[Maple Mono](https://font.subf.dev/en/):** Main font
- **Noto Color Emoji:** Emoji support in terminals

## 🤝 Contributing

Feel free to:

- Fork this repository
- Add your own configurations
- Submit improvements via pull requests
- Share your dotfiles setup!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
