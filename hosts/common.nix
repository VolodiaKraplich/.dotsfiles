{ pkgs, ... }:
{
  imports = [
    ../modules/core
    ../modules/development
    ../modules/shell
    ../modules/system
  ];

  home = {
    stateVersion = "25.11";
  };

  nixpkgs.config.allowUnfree = true;
  programs.home-manager.enable = true;

  # Common packages
  home.packages = with pkgs; [
    curl
    wget
    tree
    unzip
    git
  ];
}
