{ ... }:

{
  xdg.configFile."rio/config.toml".text = ''
    theme = "catppuccin-mocha"
    hide-mouse-cursor-when-typing = true
    confirm-before-quit = false

    [fonts]
    size = 18
    family = "Maple Mono"
    hinting = false

    [editor]
    program = "helix"
    args = []

    [cursor]
    shape = "block"
    blinkig = false

    [window]
    opacity = 1
    blur = true
  '';

  xdg.configFile."rio/themes/catppuccin-mocha.toml".text = ''
    [colors]

    # Normal
    foreground       = '#cdd6f4'
    background       = '#1e1e2e'
    black            = '#45475a'
    blue             = '#89b4fa'
    cursor           = '#f5e0dc'
    cyan             = '#94e2d5'
    green            = '#a6e3a1'
    magenta          = '#f5c2e7'
    red              = '#f38ba8'
    white            = '#bac2de'
    yellow           = '#f9e2af'

    # UI colors
    tabs             = '#1e1e2e'
    tabs-foreground  = '#cdd6f4'
    tabs-active      = '#b4befe'
    tabs-active-highlight  = '#b4befe'
    tabs-active-foreground = '#11111b'
    selection-foreground   = '#1e1e2e'
    selection-background   = '#f5e0dc'

    # Dim colors
    dim-black        = '#45475a'
    dim-blue         = '#89b4fa'
    dim-cyan         = '#94e2d5'
    dim-foreground   = '#cdd6f4'
    dim-green        = '#a6e3a1'
    dim-magenta      = '#f5c2e7'
    dim-red          = '#f38ba8'
    dim-white        = '#bac2de'
    dim-yellow       = '#f9e2af'

    # Light colors
    light-black      = '#585b70'
    light-blue       = '#89b4fa'
    light-cyan       = '#94e2d5'
    light-foreground = '#cdd6f4'
    light-green      = '#a6e3a1'
    light-magenta    = '#f5c2e7'
    light-red        = '#f38ba8'
    light-white      = '#a6adc8'
    light-yellow     = '#f9e2af'
  '';

}
