let
  nixpkgs = builtins.fetchTarball {
    name = "nixpkgs-unstable-thefractal.space";
    url = "https://github.com/NixOS/nixpkgs-channels/archive/b61999e4ad60c351b4da63ae3ff43aae3c0bbdfb.tar.gz";
    sha256 = "0cggpdks4qscyirqwfprgdl91mlhjlw24wkg0riapk5f2g2llbpq";
  };
in
{ pkgs ? import nixpkgs {}, mkEnv ? false }:

with pkgs;

(if mkEnv then poetry2nix.mkPoetryEnv else poetry2nix.mkPoetryApplication) {
  projectDir = ./.;
  overrides = poetry2nix.overrides.withDefaults (self: super: {
    kivy = null;
    kivymd = null;
    kivy-garden = null;
    colour = super.colour.overridePythonAttrs(old: {
      buildInputs = [ python3Packages.d2to1 ];
    });
  });
}
