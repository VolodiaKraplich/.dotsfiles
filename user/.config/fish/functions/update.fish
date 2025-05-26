function update --description "Update system packages based on available package manager"
    # Choose the appropriate package manager and prepare the command
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
