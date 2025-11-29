{ pkgs }:

pkgs.mkShell {
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.opencv
    pkgs.python311Packages.pytesseract
    pkgs.python311Packages.pillow
    pkgs.python311Packages.numpy
  ];
}