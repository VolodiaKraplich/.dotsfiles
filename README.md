# Configuration Scripts for My Dots

A minimal yet powerful dotfiles repository to automate Linux system setup.

## 🌟 Features

- **Fish Shell**
  - Git-integrated prompt
  - Aliases & modern replacements: `eza`, `bat`
  - Git helpers (`gf`) & command notifications

- **Dev Tools**
  - Git defaults & global ignore patterns
  - Editor configs (Helix Editor)

- **System**
  - AMDGPU optimizations
  - ZRAM setup (12GB, ZSTD)
  - Backup mechanism

- **Terminal**
  - Rio + Catppuccin Mocha theme
  - Maple Mono
  - Custom "command not found" handler

## 📁 Structure

```
Configuration/
├── system/              # System-wide configs
│   ├── etc/amdgpu.conf
│   └── systemd/zram-generator.conf
└── user/                # User-specific configs
    ├── .config/
    │   ├── fastfetch
    │   ├── fish
    │   ├── rio
    │   ├── git
    │   ├── helix
    │   └── starship.toml
    └── patches/
```

## 🚀 Installation

```bash
git clone https://github.com/VolodiaKraplich/.dotsfiles.git --depth=1
cd .dotsfiles
./install.sh
```

**Options:**  
`--no-bak` – skip backups  
`--no-sys` – skip system configs

## ⚙️ Requirements

- Fish shell 4.0+
- Deps: `eza`, `bat`, `git`, `starship`

## 🤝 Contributing
Pull requests are welcome!

## 📝 License

[MIT License](./LICENSE)
