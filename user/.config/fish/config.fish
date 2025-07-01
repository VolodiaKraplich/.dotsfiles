# ------------------------------------------------------------------------------
# Starship Prompt Initialization
# ------------------------------------------------------------------------------
starship init fish | source
# ------------------------------------------------------------------------------
# General Fish Shell Settings
# ------------------------------------------------------------------------------

# Disable fish greeting message
function fish_greeting
end
set -g fish_greeting

# Load Catppuccin Mocha theme
set -g fish_color_normal cdd6f4
set -g fish_color_command 89b4fa
set -g fish_color_param f2cdcd
set -g fish_color_keyword f38ba8
set -g fish_color_quote a6e3a1
set -g fish_color_redirection f5c2e7
set -g fish_color_end fab387
set -g fish_color_comment 7f849c
set -g fish_color_error f38ba8
set -g fish_color_gray 6c7086
set -g fish_color_selection --background=313244
set -g fish_color_search_match --background=313244
set -g fish_color_option a6e3a1
set -g fish_color_operator f5c2e7
set -g fish_color_escape eba0ac
set -g fish_color_autosuggestion 6c7086
set -g fish_color_cancel f38ba8
set -g fish_color_cwd f9e2af
set -g fish_color_user 94e2d5
set -g fish_color_host 89b4fa
set -g fish_color_host_remote a6e3a1
set -g fish_color_status f38ba8
set -g fish_pager_color_progress 6c7086
set -g fish_pager_color_prefix f5c2e7
set -g fish_pager_color_completion cdd6f4
set -g fish_pager_color_description 6c7086

# Format man pages with bat for colored output
set -x MANPAGER "sh -c 'col -bx | bat -l man -p'"

# Isolate command history for containers to avoid polluting the host's history
if test "$container" = "podman" -o "$container" = "docker" -o -n "$DISTROBOX_ENTER_PATH"
    set -g fish_history ""
end

# ------------------------------------------------------------------------------
# Aliases (Shortcuts for common commands)
# ------------------------------------------------------------------------------

# Directory Navigation
alias .. "cd .."
alias ... "cd ../.."
alias .... "cd ../../.."

# Modern Unix command replacements
if type -q eza
    alias ls "eza -al --color=always --group-directories-first --icons" # full listing
    alias l "eza -l --color=always --group-directories-first --icons"    # long format
    alias la "eza -a --color=always --group-directories-first --icons"   # all files
    alias lt "eza -aT --color=always --group-directories-first --icons"  # tree view
    alias tree "eza --tree"
end

if type -q bat
    alias cat "bat --theme=Catppuccin-mocha"
end

# Other useful aliases
alias untar "tar -xvf"
alias tarnow "tar -acf"
alias grep "grep --color=auto"
alias wget "wget -c"

# Git aliases
if type -q git
    alias g "git"
    alias ga "git add"
    alias gc "git commit"
    alias gco "git checkout"
    alias gd "git diff"
    alias gs "git status"
    alias gl "git log --oneline --graph --decorate"
    alias gp "git push"
    alias gpull "git pull"
    alias gb "git branch"
end

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

# Function for `!!` (repeat previous command) and `!$` (last argument)
# This brings useful functionality from Bash to Fish.
function __history_previous_command
  switch (commandline -t)
    case "!"
      commandline -t $history[1]; commandline -f repaint
    case "*"
      commandline -i !
  end
end

function __history_previous_command_arguments
    switch (commandline -t)
        case "!"
            commandline -t ""
            commandline -f history-token-search-backward
        case "*"
            commandline -i '$'
    end
end

# Bind the functions to the ! and $ keys
if [ "$fish_key_bindings" = "fish_vi_key_bindings" ]
    bind -Minsert ! __history_previous_command
    bind -Minsert '$' __history_previous_command_arguments
else
    bind ! __history_previous_command
    bind '$' __history_previous_command_arguments
end

# Display timestamps in command history
function history
    builtin history --show-time='%F %T '
end

# Simple function to create a backup of a file
function backup --argument filename
    cp $filename $filename.bak
end

# ------------------------------------------------------------------------------
# Plugin Settings (e.g., "done")
# ------------------------------------------------------------------------------

# Settings for the "done" plugin (desktop notifications for long commands)
set -g __done_min_cmd_duration 10000       # Notify after 10 seconds
set -g __done_exclude '^git (?!push|pull|fetch)'  # Don't notify for most git commands
set -g __done_notify_sound 0               # No sound with notifications
set -g __done_notification_duration 3000   # How long notifications stay on screen (ms)
set -U __done_notification_urgency_level low # Set urgency level to low
