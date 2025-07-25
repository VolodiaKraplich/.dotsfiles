{ ... }:
{

  xdg.configFile."helix/config.toml".text = ''
    theme = "catppuccin_mocha"

    # =============================================================================
    # Editor Configuration
    # =============================================================================

    [editor]
    bufferline = "multiple"
    color-modes = true
    idle-timeout = 0
    line-number = "relative"
    mouse = true
    scrolloff = 999
    true-color = true

    [editor.cursor-shape]
    insert = "bar"
    normal = "block"
    select = "underline"

    [editor.file-picker]
    git-global = false # show files hidden by git globally
    hidden = false     # show hidden files as in starting with a dot

    [editor.indent-guides]
    character = "|"
    render = true
    skip-levels = 1

    [editor.lsp]
    display-inlay-hints = true
    display-messages = true

    [editor.soft-wrap]
    enable = true

    # =============================================================================
    # Theme & UI
    # =============================================================================

    [editor.statusline]
    mode.insert = "INSERT"
    mode.normal = "NORMAL"
    mode.select = "SELECT"
    left = [
      "mode",
      "spacer",
      "version-control",
      "spacer",
      "separator",
      "file-name",
      "file-modification-indicator",
    ]
    right = [
      "spinner",
      "spacer",
      "workspace-diagnostics",
      "separator",
      "spacer",
      "diagnostics",
      "position",
      "file-encoding",
      "file-line-ending",
      "file-type",
    ]
  '';

  xdg.configFile."helix/languages.toml".text = ''
    # =============================================================================
    # Languages
    # =============================================================================

    [[language]]
    name = "rust"
    scope = "source.rust"
    injection-regex = "rs|rust"
    file-types = ["rs"]
    roots = ["Cargo.toml", "Cargo.lock"]
    shebangs = ["rust-script", "cargo"]
    auto-format = true
    formatter = { command = "rustfmt" }
    comment-tokens = ["//", "///", "//!"]
    block-comment-tokens = [
      { start = "/*", end = "*/" },
      { start = "/**", end = "*/" },
      { start = "/*!", end = "*/" },
    ]
    indent = { tab-width = 2, unit = "    " }
    persistent-diagnostic-sources = ["rustc", "clippy"]

    [language.auto-pairs]
    '(' = ')'
    '{' = '}'
    '[' = ']'
    '"' = '"'
    '`' = '`'

    [[language]]
    name = "tsx"
    scope = "source.tsx"
    injection-regex = "(tsx)"
    language-id = "typescriptreact"
    file-types = ["tsx"]
    roots = ["package.json", "tsconfig.json"]
    comment-token = "//"
    block-comment-tokens = { start = "/*", end = "*/" }
    language-servers = ["typescript-language-server"]
    indent = { tab-width = 2, unit = "  " }

    [[language]]
    name = "typescript"
    scope = "source.ts"
    injection-regex = "(ts|typescript)"
    language-id = "typescript"
    file-types = ["ts", "mts", "cts"]
    shebangs = ["deno", "bun", "ts-node"]
    roots = ["package.json", "tsconfig.json"]
    comment-token = "//"
    block-comment-tokens = { start = "/*", end = "*/" }
    language-servers = [
      "typescript-language-server",
      { name = "efm-lsp-prettier", only-features = [
        "format",
      ] },
    ]
    indent = { tab-width = 2, unit = "  " }

    # =============================================================================
    # Language Servers & Other Configurations
    # =============================================================================

    [language-server.rust-analyzer.config]
    check.command = "clippy"
    cargo.features = "all"
    files.watcher = "server"
    inlayHints.bindingModeHints.enable = false
    inlayHints.closingBraceHints.minLines = 10
    inlayHints.closureReturnTypeHints.enable = "with_block"
    inlayHints.discriminantHints.enable = "fieldless"
    inlayHints.lifetimeElisionHints.enable = "skip_trivial"
    inlayHints.typeHints.hideClosureInitialization = false
  '';
}
