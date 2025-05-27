function update --description "Update system packages based on available package manager"
  set update_cmd ""
  set pkg_manager ""

  if type -q apt
    set pkg_manager "apt"
    set update_cmd "sudo apt update && sudo apt upgrade -y"
  else if type -q paru
    set pkg_manager "paru"
    set update_cmd "paru -Syu"
  else if type -q yay
    set pkg_manager "yay"
    set update_cmd "yay -Syu"
  else if type -q pacman
    set pkg_manager "pacman"
    set update_cmd "sudo pacman -Syu"
  else if type -q dnf
    set pkg_manager "dnf"
    set update_cmd "sudo dnf up -y"
  else if type -q nobara-sync
    set pkg_manager "nobara-sync"
    set update_cmd "nobara-sync cli"
  end

  # Execute the update command if one was found, otherwise notify the user
  if test -n "$update_cmd"
    eval $update_cmd
  else
    echo "No supported package manager found."
  end
end

function cleanup --description "Clean system packages cache and remove orphaned packages"
  echo "Starting system cleanup..."

  # For Debian-based systems: use apt
  if type -q apt
    sudo apt autoremove -y
    sudo apt clean
  # For Arch-based systems: use paru, yay, or pacman
  else if type -q paru
    paru -Scc
    # paru -Qtdq lists orphaned AUR packages, pacman -Qtdq lists orphaned repo packages
    # paru -Rns can remove both types
    set -l orphaned_packages (paru -Qtdq)
    if test -n "$orphaned_packages"
      paru -Rns $orphaned_packages
    else
      echo "No orphaned packages found."
    end
  else if type -q yay
    echo "Detected yay package manager."
    echo "Running yay -Scc (clean cache)..."
    yay -Scc
    # yay -Qtdq lists orphaned AUR packages, pacman -Qtdq lists orphaned repo packages
    # yay -Rns can remove both types
    set -l orphaned_packages (yay -Qtdq)
    if test -n "$orphaned_packages"
      yay -Rns $orphaned_packages
    else
      echo "No orphaned packages found."
    end
  else if type -q pacman
    sudo pacman -Scc
    # pacman -Qtdq lists orphaned repo packages
    set -l orphaned_packages (pacman -Qtdq)
    if test -n "$orphaned_packages"
      sudo pacman -Rns $orphaned_packages
    else
      echo "No orphaned repo packages found."
    end
    # For Nobara: use nobara-sync for cache clean and dnf for autoremove
  else if type -q nobara-sync
    nobara-sync clean-dnf
    # Assuming Nobara still uses dnf for autoremove of explicitly installed packages
    sudo dnf autoremove -y
    # For Fedora-based systems: use dnf
  else if type -q dnf
    sudo dnf autoremove -y
    sudo dnf clean all
  else
    echo "No supported package manager found for cleanup."
  end

  echo "Cleanup finished."
end
