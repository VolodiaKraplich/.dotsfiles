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
      key = "002ABD09FDBDD50C";
      signByDefault = true;
    };
  };

}
