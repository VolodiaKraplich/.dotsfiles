{
  programs.fastfetch = {
    enable = true;
    settings = {
      logo = {
        source = "linux_small";
        height = 18;
        padding.top = 1;
      };
      display.separator = " ";
      modules = [
        "break"
        {
          type = "title";
          keyWidth = 10;
        }
        {
          type = "os";
          key = "OS:";
          keyColor = "33";
        }
        {
          type = "kernel";
          key = "KERNEL:";
          keyColor = "33";
        }
        {
          type = "host";
          format = "{5} {1}";
          key = "HOST:";
          keyColor = "33";
        }
        {
          type = "packages";
          format = "{}";
          key = "PKGS:";
          keyColor = "33";
        }
        {
          type = "uptime";
          format = "{2}h {3}m";
          key = "UPTIME:";
          keyColor = "33";
        }
        {
          type = "memory";
          key = "RAM:";
          keyColor = "33";
        }
        {
          type = "custom";
          # Use fastfetch's built-in color formatting
          # {#} resets the color
          format = "{#90}  {#31}  {#32}  {#33}  {#34}  {#35}  {#36}  {#37}{#}";
        }
        "break"
      ];
    };
  };
}
