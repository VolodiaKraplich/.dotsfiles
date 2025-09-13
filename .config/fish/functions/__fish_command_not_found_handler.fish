function __fish_command_not_found_handler --on-event fish_command_not_found
  set cmd "$argv[1]"

  if type -q command_exists
    if command_exists "$cmd"
      return
    end
  end

  set_color --bold red
  echo "Command '$cmd' not found."
  set_color normal
end
