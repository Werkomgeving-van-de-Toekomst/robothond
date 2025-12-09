#!/bin/bash

echo "=========================================="
echo "  Setup Virtual Environment met Python 3.12"
echo "=========================================="
echo ""

# Check of Python 3.12 beschikbaar is
if ! command -v python3.12 &> /dev/null
then
    echo "❌ Python 3.12 niet gevonden!"
    echo ""
    echo "Installeer Python 3.12 via Homebrew:"
    echo "  brew install python@3.12"
    echo ""
    exit 1
fi

echo "✓ Python 3.12 gevonden: $(python3.12 --version)"
echo ""

# Verwijder oude venv als die bestaat
if [ -d "venv" ]; then
    echo "⚠️  Oude venv gevonden. Verwijderen..."
    rm -rf venv
fi

# Maak nieuwe venv met Python 3.12
echo "📦 Maak nieuwe virtual environment met Python 3.12..."
python3.12 -m venv venv

# Activeer venv
echo "🔌 Activeer virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrade pip..."
pip install --upgrade pip

# Installeer dependencies
echo "📥 Installeer dependencies..."
pip install -r requirements.txt

# Check CYCLONEDDS_HOME
if [ -z "$CYCLONEDDS_HOME" ]; then
    echo ""
    echo "⚠️  CYCLONEDDS_HOME niet gezet!"
    echo ""
    echo "Voor officiële SDK, installeer eerst CycloneDDS:"
    echo "  ./install_cyclonedds_macos.sh"
    echo ""
    echo "Of export handmatig:"
    echo "  export CYCLONEDDS_HOME=\"/Users/marc/cyclonedds/install\""
    echo ""
else
    echo "✓ CYCLONEDDS_HOME gezet: $CYCLONEDDS_HOME"
    
    # Probeer cyclonedds te installeren
    echo "📥 Installeer cyclonedds..."
    pip install cyclonedds==0.10.2 || echo "⚠️  cyclonedds installatie mislukt (check CYCLONEDDS_HOME)"
fi

echo ""
echo "=========================================="
echo "  ✅ Setup Compleet!"
echo "=========================================="
echo ""
echo "Activeer de virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "Test de setup:"
echo "  python src/examples/first_time_setup_test.py --skip-robot"
echo ""


