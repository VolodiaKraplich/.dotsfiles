{ ... }:
{
  imports = [
    ../common.nix
    ../../modules/desktop
  ];

  home = {
    username = "volodia";
    homeDirectory = "/home/volodia";
  };

  programs.git = {
    enable = true;
    userName = "Volodia Kraplich";
    userEmail = "v1mkss.m+git@gmail.com";

    signing = {
      key = "6063DD2C68F2CEFA";
      signByDefault = true;
    };
  };

}
