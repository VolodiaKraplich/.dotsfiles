#!/bin/bash

# Check if the OS is Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
  echo "This script is intended for Linux systems."
  exit 1
fi

# Parse command-line arguments for --no-bak and --no-sys
NO_BAK=false
NO_SYS=false
for arg in "$@"; do
  if [ "$arg" == "--no-bak" ]; then
    NO_BAK=true
  elif [ "$arg" == "--no-sys" ]; then
    NO_SYS=true
  fi
done

# Detect Linux distribution
if [ -f /etc/os-release ]; then
  . /etc/os-release
  DISTRO_ID=${ID,,}
  DISTRO_LIKE=${ID_LIKE,,}
else
  echo "Cannot determine Linux distribution."
  exit 1
fi

echo "Detected distribution: $NAME"

# Function to install python
install_python() {
  case "$1" in
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
      echo "Automatic Python installation is not supported for this distribution."
      return 1
      ;;
  esac
}

# Check if Python is installed
if command -v python3 &>/dev/null; then
  PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
  PYTHON_BIN="python"
else
  echo "Python is not installed."
  read -p "Do you want to install Python now? [Y/n]: " INSTALL_PY
  INSTALL_PY=${INSTALL_PY:-Y}
  if [[ "$INSTALL_PY" =~ ^[Yy]$ ]]; then
    if [[ "$DISTRO_ID" =~ (debian|ubuntu|linuxmint) || "$DISTRO_LIKE" =~ debian ]]; then
      install_python debian
    elif [[ "$DISTRO_ID" =~ (fedora|nobara) || "$DISTRO_LIKE" =~ fedora ]]; then
      install_python fedora
    elif [[ "$DISTRO_ID" =~ (opensuse|suse) || "$DISTRO_LIKE" =~ suse ]]; then
      install_python opensuse
    elif [[ "$DISTRO_ID" =~ (arch|manjaro|endeavouros) || "$DISTRO_LIKE" =~ arch ]]; then
      install_python arch
    else
      install_python unknown
    fi
    # Re-check python after install
    if command -v python3 &>/dev/null; then
      PYTHON_BIN="python3"
    elif command -v python &>/dev/null; then
      PYTHON_BIN="python"
    else
      echo "Python installation failed or not found in PATH."
      exit 1
    fi
  else
    echo "Python is required. Exiting."
    exit 1
  fi
fi

PYTHON_VERSION=$($PYTHON_BIN --version 2>&1)
echo "Python found: $PYTHON_VERSION"

# 1. Copy user .config to $HOME
if [ -d "user/.config" ]; then
  cp -r user/.config "$HOME"
  echo ".config directory from user copied to $HOME"
else
  echo "user/.config directory not found"
fi

# 2. Run all python patches for user
if [ -d "user/patches" ]; then
  for patch in user/patches/*.py; do
    if [ -f "$patch" ]; then
      echo "Running patch: $patch"
      $PYTHON_BIN "$patch"
    fi
  done
else
  echo "user/patches directory not found"
fi

# 3. Copy system files (with backup if exists) to root (/)
if [ "$NO_SYS" = false ]; then
  if [ -d "system" ]; then
    echo "Copying system files (with backup if exists)..."
    find system -type f | while read SRC; do
      REL_PATH="${SRC#system/}"
      DEST="/${REL_PATH}"

      if [ -f "$DEST" ] && [ "$NO_BAK" = false ]; then
        BACKUP="${DEST}.bak"
        echo "Backing up $DEST to $BACKUP"
        sudo cp -f "$DEST" "$BACKUP"
      fi

      echo "Copying $SRC to $DEST"
      sudo cp "$SRC" "$DEST"
    done
  else
    echo "system directory not found"
  fi
else
  echo "--no-sys option provided, skipping copying system files."
fi

exit 0
