#!/bin/bash
# Script om Miniconda te installeren voor PyBullet

echo "=========================================="
echo "  Miniconda Installatie voor PyBullet"
echo "=========================================="
echo ""

# Check of conda al bestaat
if command -v conda &> /dev/null; then
    echo "✓ Conda is al geïnstalleerd!"
    conda --version
    exit 0
fi

# Check of er al een conda installatie is
if [ -d "$HOME/miniconda3" ] || [ -d "$HOME/anaconda3" ]; then
    echo "⚠️  Conda directory gevonden maar niet in PATH"
    echo "   Voeg toe aan ~/.zshrc:"
    echo "   export PATH=\"\$HOME/miniconda3/bin:\$PATH\""
    echo "   of:"
    echo "   export PATH=\"\$HOME/anaconda3/bin:\$PATH\""
    exit 1
fi

echo "Miniconda wordt gedownload en geïnstalleerd..."
echo ""

# Download URL voor macOS ARM64
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
else
    URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
fi

INSTALLER="$HOME/miniconda_installer.sh"

echo "Downloaden van Miniconda..."
curl -L -o "$INSTALLER" "$URL"

if [ $? -ne 0 ]; then
    echo "❌ Download mislukt"
    exit 1
fi

echo ""
echo "Installeren van Miniconda..."
echo "Dit kan even duren..."
bash "$INSTALLER" -b -p "$HOME/miniconda3"

if [ $? -ne 0 ]; then
    echo "❌ Installatie mislukt"
    rm -f "$INSTALLER"
    exit 1
fi

# Cleanup
rm -f "$INSTALLER"

# Initialize conda
"$HOME/miniconda3/bin/conda" init zsh

echo ""
echo "✓ Miniconda geïnstalleerd!"
echo ""
echo "Herstart je terminal of voer uit:"
echo "  source ~/.zshrc"
echo ""
echo "Dan kun je PyBullet installeren met:"
echo "  conda create -n pybullet python=3.9"
echo "  conda activate pybullet"
echo "  conda install -c conda-forge pybullet numpy"

