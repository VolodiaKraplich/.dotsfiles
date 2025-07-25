{
  description = "Home Manager configuration for Arch Linux";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    zen-browser = {
      url = "github:0xc000022070/zen-browser-flake";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      home-manager,
      ...
    }@inputs:
    {
      homeConfigurations = {
        # Current laptop
        "user@laptop" = home-manager.lib.homeManagerConfiguration {
          pkgs = nixpkgs.legacyPackages.x86_64-linux;
          modules = [
            ./hosts/laptop/home.nix
          ];

          extraSpecialArgs = { inherit inputs; };
        };

        # Future server
        # "user@server" = home-manager.lib.homeManagerConfiguration {
        #   pkgs = nixpkgs.legacyPackages.x86_64-linux;
        #   modules = [
        #     ./hosts/server/home.nix
        #   ];
        #   extraSpecialArgs = { inherit inputs; };
        # };
      };
    };
}
