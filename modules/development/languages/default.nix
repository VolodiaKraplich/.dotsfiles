{ pkgs, ... }:
{
  home.packages = with pkgs; [
    nil # Nix LSP
    taplo # TOML LSP
    yaml-language-server # Yaml
    vscode-langservers-extracted # HTML, CSS, JSON, ESLint LSPs

    # Formaters
    prettier
    stylua # Lua formatter
  ];
}
