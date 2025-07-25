{
  programs.starship = {
    enable = true;
    # The starship.toml file is generated from this settings block.
    settings = {
      # Quoted key because '$' is a special character in Nix.
      "$schema" = "https://starship.rs/config-schema.json";

      # Use indented strings ('') for format strings to prevent Nix from
      # trying to interpret variables like $username.
      format = ''$username$directory$line_break[└─>$character](bold green)'';

      add_newline = false;
      continuation_prompt = "[ ](bold green)";
      palette = "catppuccin_mocha";

      # --- Modules ---
      character = {
        success_symbol = "[>](bold green)";
        error_symbol = "[>](bold red)";
      };

      username = {
        style_user = "bold mauve";
        style_root = "bold red";
        format = ''[$user]($style) '';
        show_always = true;
      };

      hostname = {
        disabled = true;
      };

      directory = {
        style = "bold blue";
        truncation_length = 3;
        truncation_symbol = "…/";
        read_only = " 🔒";
        read_only_style = "red";
        format = ''in [$path]($style)[$read_only]($read_only_style)'';
      };

      git_branch = {
        style = "bold yellow";
        format = ''on [$branch]($style) '';
      };

      git_status = {
        style = "bold yellow";
        # For strings with backslashes, use double quotes and escape the backslash.
        staged = "[++\\($count\\)](green) ";
        format = ''([$ahead_behind]($style))'';
      };

      cmd_duration = {
        min_time = 5000; # Underscores from TOML numbers are removed.
        style = "bold yellow";
        format = ''took [$duration]($style) '';
      };

      # --- Built-in modules for environments ---
      aws = {
        symbol = " ";
        style = "bold yellow";
        format = ''on [$symbol$profile]($style) '';
      };

      kubernetes = {
        symbol = " ";
        style = "bold yellow";
        format = ''on [$symbol$context\($namespace\)]($style) '';
      };

      container = {
        symbol = " ";
        style = "bold yellow";
        format = ''in [$symbol$name]($style) '';
      };

      time = {
        disabled = true;
        style = "bold text";
        format = ''at [$time]($style) '';
      };

      package.disabled = true;
      rust.disabled = true;

      # --- Palettes ---
      palettes = {
        catppuccin_mocha = {
          rosewater = "#f5e0dc";
          flamingo = "#f2cdcd";
          pink = "#f5c2e7";
          mauve = "#cba6f7";
          red = "#f38ba8";
          maroon = "#eba0ac";
          peach = "#fab387";
          yellow = "#f9e2af";
          green = "#a6e3a1";
          teal = "#94e2d5";
          sky = "#89dceb";
          sapphire = "#74c7ec";
          blue = "#89b4fa";
          lavender = "#b4befe";
          text = "#cdd6f4";
          subtext1 = "#bac2de";
          subtext0 = "#a6adc8";
          overlay2 = "#9399b2";
          overlay1 = "#7f849c";
          overlay0 = "#6c7086";
          surface2 = "#585b70";
          surface1 = "#45475a";
          surface0 = "#313244";
          base = "#1e1e2e";
          mantle = "#181825";
          crust = "#11111b";
        };
      };
    };
  };
}
