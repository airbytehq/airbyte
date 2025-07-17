#!/usr/bin/env bash
# Make a portable tar for the connector
set -euo pipefail

# Config
JAVA_VERSION="21"
CONNECTOR_NAME="$(basename "$PWD")"
BUILD_DIR="build"
TMP_DIR="$BUILD_DIR/tmp"
AZUL_API_URL="https://api.azul.com/metadata/v1/zulu/packages/?java_version=${JAVA_VERSION}&os=linux&arch=x64&java_package_type=jre&release_status=ga&availability_types=CA"
JAR_ROOT_NAME="airbyte-app"
# JAR_ROOT_NAME=$CONNECTOR_NAME # << Should be this
DIST_TAR="$BUILD_DIR/distributions/${JAR_ROOT_NAME}.tar"
PORTABLE_TAR="$BUILD_DIR/distributions/${CONNECTOR_NAME}.portable.tar"
JRE_DIR="$TMP_DIR/${JAR_ROOT_NAME}/java/jre"

# 1. Build connector tar
echo "🔨 Building distTar for $CONNECTOR_NAME..."
../../../gradlew ":airbyte-integrations:connectors:$CONNECTOR_NAME:distTar"

# 2. Write launch.sh
mkdir -p "$TMP_DIR/${JAR_ROOT_NAME}/bin"
cat > "$TMP_DIR/${JAR_ROOT_NAME}/bin/portable-launch.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CONNECTOR_NAME="source-mssql" # Obviously not portable, but this is just to unblock testing

# Default: where to cache downloaded JREs
JRE_CACHE_DIR="${BASE_DIR}/.jre-cache"

# --- Step 1: Use JAVA_HOME if available
if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/java" ]]; then
  echo "✅ Using JAVA from JAVA_HOME: $JAVA_HOME"
  JAVA="$JAVA_HOME/bin/java"

# --- Step 2: Use bundled JRE if present
elif [[ -x "$BASE_DIR/jre/bin/java" ]]; then
  echo "✅ Using bundled JRE: $BASE_DIR/jre"
  JAVA="$BASE_DIR/jre/bin/java"

# --- Step 3: Download a portable JRE
else
  echo "🌐 JAVA not found — downloading portable JRE..."

  # Detect platform
  OS=$(uname -s | tr '[:upper:]' '[:lower:]')
  ARCH=$(uname -m)

  # Normalize
  if [[ "$ARCH" == "arm64" || "$ARCH" == "aarch64" ]]; then
    ARCH="aarch64"
  elif [[ "$ARCH" == "x86_64" ]]; then
    ARCH="x64"
  else
    echo "❌ Unsupported architecture: $ARCH"
    exit 1
  fi

  if [[ "$OS" == "darwin" ]]; then
    OS="macos"
  elif [[ "$OS" != "linux" ]]; then
    echo "❌ Unsupported OS: $OS"
    exit 1
  fi

  JRE_DOWNLOAD_DIR="$JRE_CACHE_DIR/${OS}-${ARCH}"
  JAVA="$JRE_DOWNLOAD_DIR/bin/java"

  if [[ ! -x "$JAVA" ]]; then
    echo "⬇️  Downloading Zulu JRE 21 for $OS/$ARCH..."
    mkdir -p "$JRE_DOWNLOAD_DIR"

    # Query Azul API for latest version
    AZUL_API_URL="https://api.azul.com/metadata/v1/zulu/packages/?java_version=21&os=$OS&arch=$ARCH&java_package_type=jre&release_status=ga&availability_types=CA"
    AZUL_JSON=$(curl -sSL "$AZUL_API_URL")
    JRE_URL=$(echo "$AZUL_JSON" | jq -r '[.[] | select(.download_url | endswith(".tar.gz"))][0].download_url')

    if [[ -z "$JRE_URL" || "$JRE_URL" == "null" ]]; then
      echo "❌ Failed to resolve JRE URL for $OS/$ARCH"
      exit 1
    fi

    curl -sSL "$JRE_URL" | tar -xz -C "$JRE_DOWNLOAD_DIR" --strip-components=1
  else
    echo "✅ Reusing cached JRE: $JRE_DOWNLOAD_DIR"
  fi
fi

# --- Launch connector
JAR_ROOT_NAME="airbyte-app"
JAR_PATH="$BASE_DIR/bin/source-mssql"
# JAR_PATH="$(find "$BASE_DIR/lib" -name '${JAR_ROOT_NAME}.jar' | head -n 1)"
if [[ ! -f "$JAR_PATH" ]]; then
  echo "❌ No JAR file found in $BASE_DIR/lib"
  exit 1
fi

echo "🚀 Running connector via: $BASE_DIR/bin/$CONNECTOR_NAME"
JAVA_HOME_DIR="$(dirname "$(dirname "$JAVA")")"

exec env JAVA_HOME="$JAVA_HOME_DIR" PATH="$JAVA_HOME_DIR/bin:$PATH" \
  "$BASE_DIR/bin/$CONNECTOR_NAME" "$@"
EOF
chmod +x "$TMP_DIR/${JAR_ROOT_NAME}/bin/portable-launch.sh"

# 3. Copy original tar to portable tar
echo "📦 Copying './$DIST_TAR' to './$PORTABLE_TAR'..."
cp "./$DIST_TAR" "./$PORTABLE_TAR"

# 4. Add portable-launch.sh to tar
echo "➕ Appending portable-launch.sh..."
tar -rf "./$PORTABLE_TAR" -C "$TMP_DIR" ${JAR_ROOT_NAME}/bin/portable-launch.sh

# 5. Download JRE from Azul API
echo "🌐 Querying Azul API for latest Zulu JRE $JAVA_VERSION..."
AZUL_META_PATH="$TMP_DIR/zulu-jre-index.json"
curl -sSL "$AZUL_API_URL" -o "$AZUL_META_PATH"

echo "📄 Saved Azul metadata to: $AZUL_META_PATH"
# echo "🔍 Preview of metadata:"
# jq '.' "$AZUL_META_PATH" | head -n 20
# echo "..."

# Extract the first package link from the array (fix jq path if needed)
JRE_URL=$(jq -r '[.[] | select(.download_url | endswith(".tar.gz"))][0].download_url' "$AZUL_META_PATH")
echo "🔗 JRE download URL: $JRE_URL"
echo "⬇️  Downloading JRE from: $JRE_URL"
mkdir -p "$JRE_DIR"
curl -sSL "$JRE_URL" | tar -xz -C "$JRE_DIR" --strip-components=1

# 6. Add JRE directory to tar
echo "➕ Appending JRE to portable tar..."
tar -rf "$PORTABLE_TAR" -C "$TMP_DIR" ${JAR_ROOT_NAME}/java/jre

echo "✅ Done! Created: $PORTABLE_TAR"

# 7. Extract and test run
echo "🧪 Verifying extracted connector..."

TEST_DIR="$BUILD_DIR/test_run"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

# Extract
tar -xf "$PORTABLE_TAR" -C "$TEST_DIR"

# Unset potentially conflicting env vars
unset JAVA_HOME
unset JAVA_OPTS

# Run spec
echo "🔧 Running 'spec'..."
"$TEST_DIR/airbyte-app/bin/portable-launch.sh" --spec
