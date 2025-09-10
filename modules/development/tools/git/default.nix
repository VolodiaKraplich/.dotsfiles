{ ... }:
{

  imports = [ ./lazygit.nix ];

  programs.git = {
    extraConfig = {
      init = {
        defaultBranch = "master";
      };

      core = {
        editor = "code --wait";
        autocrlf = "input";
      };

      pull = {
        rebase = true;
      };

      push = {
        autoSetupRemote = true;
      };

      color = {
        ui = true;
        status = {
          added = "green";
          changed = "yellow";
          untracked = "red";
        };
        branch = {
          current = "yellow reverse";
          local = "yellow";
          remote = "green";
        };
        diff = {
          meta = "yellow bold";
          frag = "magenta bold";
          old = "red bold";
          new = "green bold";
        };
      };

      commit = {
        gpgsign = true;
      };

      tag = {
        gpgSign = true;
      };
    };

    # Глобальний gitignore
    ignores = [
      # OS specific
      ".DS_Store"
      "Thumbs.db"

      # Editors
      ".idea/"
      ".vscode/"
      ".zed/"
      ".helix/"
      "*.swp"
      "*.swo"
      "*~"

      # Build outputs
      "dist/"
      "build/"
      "target/"
      "*.class"
      "*.o"

      # Dependencies
      "node_modules/"
      ".pnp/"
      ".pnp.js"
      "vendor/"

      # Environment
      ".env"
      ".env.local"
      ".env.development.local"
      ".env.test.local"
      ".env.production.local"

      # Logs
      "*.log"
      "npm-debug.log*"
      "yarn-debug.log*"
      "yarn-error.log*"

      # Coverage directories
      "coverage/"
      ".nyc_output/"

      # Cache
      ".cache/"
      ".npm/"
      ".eslintcache"
    ];
  };
}
