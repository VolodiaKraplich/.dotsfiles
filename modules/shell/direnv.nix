{pkgs, ...}:
{
  programs.direnv.enable = true;
  home.packages = [pkgs.devenv];
}
