#!/usr/bin/bash

echo "$0: Building Rust modules at $(date)"

# ==============================================================================
# 🔥 I N I T I A L I Z E
# ==============================================================================

set -eu || set -o errexit && set -o nounset; set -o pipefail; set +o history

cd "$(dirname "$0")"
DIVIDER="$(printf '=%.0s' {1..80})" && div() { echo "$DIVIDER"; }

# ==============================================================================
# 🦀 R U S T  M O D U L E  B U I L D
# ==============================================================================

echo "Building Rust price calculator module..."
div

# Check if virtual environment exists and activate it
if [[ -d ./env ]]; then
  source env/bin/activate
  echo "✅ Virtual environment activated"
else
  echo "⚠️  No virtual environment found. Please run ./DEPLOY first."
  exit 1
fi

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
  echo "Installing Rust..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  source "$HOME/.cargo/env"
fi

echo "🦀 Rust version: $(rustc --version)"
echo "📦 Cargo version: $(cargo --version)"

# Build and install Rust module
cd rust_modules/price_calculator

echo "Compiling Rust module with PyO3..."
cargo build --release

echo "Installing Python module with maturin..."
pip install maturin
maturin develop --release

cd ../../

# Test the module
echo "Testing Rust module integration..."
if python -c "import price_calculator; print('🎉 Rust module loaded successfully!')" 2>/dev/null; then
  echo "✅ Rust price calculator module is ready"
else
  echo "❌ Failed to load Rust module"
  exit 1
fi

deactivate
echo "✅ Build completed successfully!"

# ==============================================================================
# 🧷 R E F E R E N C E S
# ==============================================================================

# - https://pyo3.rs/
# - https://github.com/PyO3/maturin
# - https://doc.rust-lang.org/cargo/