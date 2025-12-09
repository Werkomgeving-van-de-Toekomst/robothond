#!/bin/bash
# Install CycloneDDS op macOS voor unitree_sdk2_python

set -e

echo "=========================================="
echo "  CycloneDDS Installatie voor macOS"
echo "=========================================="
echo ""

# Check of Homebrew geïnstalleerd is
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew niet gevonden. Installeer eerst Homebrew:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✓ Homebrew gevonden"
echo ""

# Installeer dependencies
echo "📦 Installeer build dependencies..."
brew install cmake pkg-config

# Clone CycloneDDS
CYCLONEDDS_DIR="$HOME/cyclonedds"
if [ -d "$CYCLONEDDS_DIR" ]; then
    echo "⚠️  CycloneDDS directory bestaat al: $CYCLONEDDS_DIR"
    read -p "Verwijderen en opnieuw clonen? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$CYCLONEDDS_DIR"
    else
        echo "Gebruik bestaande directory"
    fi
fi

if [ ! -d "$CYCLONEDDS_DIR" ]; then
    echo "📥 Clone CycloneDDS repository..."
    cd "$HOME"
    git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x
fi

# Build CycloneDDS
echo "🔨 Compileer CycloneDDS..."
cd "$CYCLONEDDS_DIR"
mkdir -p build install
cd build

cmake .. -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_BUILD_TYPE=Release
cmake --build . --target install

INSTALL_DIR="$CYCLONEDDS_DIR/install"

echo ""
echo "=========================================="
echo "  CycloneDDS Gecompileerd!"
echo "=========================================="
echo ""
echo "Install directory: $INSTALL_DIR"
echo ""
echo "Voeg toe aan je shell config (.zshrc of .bash_profile):"
echo ""
echo "export CYCLONEDDS_HOME=\"$INSTALL_DIR\""
echo ""
echo "Of export nu:"
echo "export CYCLONEDDS_HOME=\"$INSTALL_DIR\""
echo ""

# Vraag of gebruiker het nu wil exporteren
read -p "Nu exporteren voor deze sessie? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    export CYCLONEDDS_HOME="$INSTALL_DIR"
    echo "✓ CYCLONEDDS_HOME gezet naar: $INSTALL_DIR"
    echo ""
    echo "Nu kun je cyclonedds installeren:"
    echo "  pip install cyclonedds==0.10.2"
else
    echo ""
    echo "Vergeet niet om CYCLONEDDS_HOME te exporteren voordat je cyclonedds installeert!"
fi


