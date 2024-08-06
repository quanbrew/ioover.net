{
  description = "Build the blog";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        gems =
          with pkgs;
          bundlerEnv {
            name = "ioover-net";
            inherit ruby;
            gemdir = ./.;
          };
      in
      {
        devShells.default = pkgs.mkShell {
          BUNDLE_FORCE_RUBY_PLATFORM = "true";
          buildInputs = with pkgs; [
            ruby.devEnv
            bundix
            zlib
            libiconv
          ];
        };
        packages.default = pkgs.stdenv.mkDerivation {
          name = "ioover-net";
          src = ./.;
          # Workaround for
          # https://talk.jekyllrb.com/t/ascii-8bit-to-utf-8-encoding-undefinedconversionerror/4165/6
          LANGUAGE = "en_US.UTF-8";
          LANG = "en_US.UTF-8";
          LC_ALL = "en_US.UTF-8";
          LOCALE_ARCHIVE = "${pkgs.glibcLocales}/lib/locale/locale-archive";

          buildInputs = with pkgs; [
            zlib
            libiconv
            ruby
            gems
          ];
          installPhase = ''
            mkdir -p $out
            jekyll build
            cp -r _site/* $out
          '';
        };
      }
    );
}
