#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
# CONNECTOR_NAME="$(basename "$BASE_DIR")"
CONNECTOR_NAME="source-mssql"
JRE_CACHE_DIR="$BASE_DIR/.jre-cache"
JAVA_VERSION="21"

if [[ 1 == 0 ]]; then
  echo "..."
# # --- Step 1: Use JAVA_HOME if available
# if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/java" ]]; then
#   echo "✅ Using JAVA from JAVA_HOME: $JAVA_HOME"
#   JAVA="$JAVA_HOME/bin/java"

# --- Step 2: Use bundled JRE if present
elif [[ -x "$BASE_DIR/jre/bin/java" ]]; then
  echo "✅ Using bundled JRE: $BASE_DIR/jre"
  JAVA="$BASE_DIR/jre/bin/java"

# --- Step 3: Download JRE on-demand
else
  echo "🌐 JAVA not found — downloading portable JRE..."

  OS=$(uname -s | tr '[:upper:]' '[:lower:]')
  ARCH=$(uname -m)

  # Normalize
  [[ "$ARCH" == "arm64" || "$ARCH" == "aarch64" ]] && ARCH="aarch64"
  [[ "$ARCH" == "x86_64" ]] && ARCH="x64"
  [[ "$OS" == "darwin" ]] && OS="macos"
  [[ "$OS" == "macos" ]] && OS="macos"
  # [[ "$OS" == "linux" ]] || { echo "❌ Unsupported OS: $OS"; exit 1; }

  JRE_DOWNLOAD_DIR="$JRE_CACHE_DIR/${OS}-${ARCH}"
  JAVA="$JRE_DOWNLOAD_DIR/bin/java"

  if [[ ! -x "$JAVA" ]]; then
    AZUL_API_URL="https://api.azul.com/metadata/v1/zulu/packages/?java_version=$JAVA_VERSION&os=$OS&arch=$ARCH&java_package_type=jre&release_status=ga&availability_types=CA"
    echo "⬇️  Downloading Zulu JRE $JAVA_VERSION for $OS/$ARCH from '$AZUL_API_URL'"
    mkdir -p "$JRE_DOWNLOAD_DIR"
    AZUL_JSON=$(curl -sSL "$AZUL_API_URL")
    JRE_URL=$(echo "$AZUL_JSON" | jq -r '[.[] | select(.download_url | endswith(".tar.gz"))][0].download_url')
    [[ -z "$JRE_URL" || "$JRE_URL" == "null" ]] && { echo "❌ Failed to resolve JRE URL"; exit 1; }
    curl -sSL "$JRE_URL" | tar -xz -C "$JRE_DOWNLOAD_DIR" --strip-components=1
  else
    echo "✅ Reusing cached JRE: $JRE_DOWNLOAD_DIR"
  fi
fi

# --- Launch
JAVA_HOME_DIR="$(dirname "$(dirname "$JAVA")")"
echo "🚀 Launching connector via: $BASE_DIR/bin/$CONNECTOR_NAME"
exec env JAVA_HOME="$JAVA_HOME_DIR" PATH="$JAVA_HOME_DIR/bin:$PATH" "$BASE_DIR/bin/$CONNECTOR_NAME" "$@"
