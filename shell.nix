with import <nixpkgs> {};
mkShell {
    buildInputs = [
        (python38.withPackages(ps: with ps; [
            ncurses
            flake8
        ]))
        shellcheck
    ];
    shellHook = ''
        . .shellhook
    '';
}
