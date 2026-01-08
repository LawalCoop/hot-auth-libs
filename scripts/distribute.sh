#!/bin/bash
set -e

echo "📤 Distributing auth-libs to projects..."
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTH_LIBS_DIR="$(dirname "$SCRIPT_DIR")"
HOT_DIR="$(dirname "$AUTH_LIBS_DIR")"

# Get current version from pyproject.toml
VERSION=$(grep '^version = ' "$AUTH_LIBS_DIR/python/pyproject.toml" | sed 's/version = "\(.*\)"/\1/')
echo "📌 Current auth-libs version: v$VERSION"
echo ""

# Distribute web component
echo "📦 Distributing web-component (source + dist) to portal..."
mkdir -p "$HOT_DIR/portal/frontend/auth-libs/web-component"
rm -rf "$HOT_DIR/portal/frontend/auth-libs/web-component/dist"
rm -rf "$HOT_DIR/portal/frontend/auth-libs/web-component/src"
cp -r "$AUTH_LIBS_DIR/web-component/dist" "$HOT_DIR/portal/frontend/auth-libs/web-component/"
cp -r "$AUTH_LIBS_DIR/web-component/src" "$HOT_DIR/portal/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/package.json" "$HOT_DIR/portal/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/vite.config.js" "$HOT_DIR/portal/frontend/auth-libs/web-component/"
echo "✅ Web component (source + dist) → portal"
echo ""

# Distribute Python package to portal
echo "📦 Distributing Python dist/ to portal..."
mkdir -p "$HOT_DIR/portal/backend/auth-libs/python"
rm -rf "$HOT_DIR/portal/backend/auth-libs/python/dist"
cp -r "$AUTH_LIBS_DIR/python/dist" "$HOT_DIR/portal/backend/auth-libs/python/"
echo "✅ Python package → portal"
echo ""

# Distribute web component to drone-tm
echo "📦 Distributing web-component (source + dist) to drone-tm..."
mkdir -p "$HOT_DIR/drone-tm/src/frontend/auth-libs/web-component"
rm -rf "$HOT_DIR/drone-tm/src/frontend/auth-libs/web-component/dist"
rm -rf "$HOT_DIR/drone-tm/src/frontend/auth-libs/web-component/src"
cp -r "$AUTH_LIBS_DIR/web-component/dist" "$HOT_DIR/drone-tm/src/frontend/auth-libs/web-component/"
cp -r "$AUTH_LIBS_DIR/web-component/src" "$HOT_DIR/drone-tm/src/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/package.json" "$HOT_DIR/drone-tm/src/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/vite.config.js" "$HOT_DIR/drone-tm/src/frontend/auth-libs/web-component/"
echo "✅ Web component (source + dist) → drone-tm"
echo ""

# Distribute Python package to drone-tm
echo "📦 Distributing Python dist/ to drone-tm..."
mkdir -p "$HOT_DIR/drone-tm/src/backend/auth-libs"
rm -rf "$HOT_DIR/drone-tm/src/backend/auth-libs/dist"
cp -r "$AUTH_LIBS_DIR/python/dist" "$HOT_DIR/drone-tm/src/backend/auth-libs/"
# Copy wheel to libs/ directory (used by pyproject.toml/uv.lock)
rm -f "$HOT_DIR/drone-tm/src/backend/libs/"hotosm_auth-*.whl
cp "$AUTH_LIBS_DIR/python/dist/"*.whl "$HOT_DIR/drone-tm/src/backend/libs/"
echo "✅ Python package → drone-tm"
echo ""

# Distribute Python package to login
echo "📦 Distributing Python dist/ to login..."
mkdir -p "$HOT_DIR/login/backend/auth-libs/python"
rm -rf "$HOT_DIR/login/backend/auth-libs/python/dist"
cp -r "$AUTH_LIBS_DIR/python/dist" "$HOT_DIR/login/backend/auth-libs/python/"
echo "✅ Python package → login"
echo ""

# Distribute web component to login
echo "📦 Distributing web-component (source + dist) to login..."
mkdir -p "$HOT_DIR/login/frontend/auth-libs/web-component"
rm -rf "$HOT_DIR/login/frontend/auth-libs/web-component/dist"
rm -rf "$HOT_DIR/login/frontend/auth-libs/web-component/src"
cp -r "$AUTH_LIBS_DIR/web-component/dist" "$HOT_DIR/login/frontend/auth-libs/web-component/"
cp -r "$AUTH_LIBS_DIR/web-component/src" "$HOT_DIR/login/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/package.json" "$HOT_DIR/login/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/vite.config.js" "$HOT_DIR/login/frontend/auth-libs/web-component/"
echo "✅ Web component (source + dist) → login"
echo ""

# Distribute web component to openaerialmap
echo "📦 Distributing web-component (source + dist) to openaerialmap..."
mkdir -p "$HOT_DIR/openaerialmap/frontend/auth-libs/web-component"
rm -rf "$HOT_DIR/openaerialmap/frontend/auth-libs/web-component/dist"
rm -rf "$HOT_DIR/openaerialmap/frontend/auth-libs/web-component/src"
cp -r "$AUTH_LIBS_DIR/web-component/dist" "$HOT_DIR/openaerialmap/frontend/auth-libs/web-component/"
cp -r "$AUTH_LIBS_DIR/web-component/src" "$HOT_DIR/openaerialmap/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/package.json" "$HOT_DIR/openaerialmap/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/vite.config.js" "$HOT_DIR/openaerialmap/frontend/auth-libs/web-component/"
echo "✅ Web component (source + dist) → openaerialmap"
echo ""

# Distribute Python package to openaerialmap
echo "📦 Distributing Python dist/ to openaerialmap..."
mkdir -p "$HOT_DIR/openaerialmap/backend/stac-api/auth-libs"
rm -rf "$HOT_DIR/openaerialmap/backend/stac-api/auth-libs/dist"
cp -r "$AUTH_LIBS_DIR/python/dist" "$HOT_DIR/openaerialmap/backend/stac-api/auth-libs/"
echo "✅ Python package → openaerialmap"
echo ""

# Distribute web component to fAIr
echo "📦 Distributing web-component (source + dist) to fAIr..."
mkdir -p "$HOT_DIR/fAIr/frontend/auth-libs/web-component"
rm -rf "$HOT_DIR/fAIr/frontend/auth-libs/web-component/dist"
rm -rf "$HOT_DIR/fAIr/frontend/auth-libs/web-component/src"
cp -r "$AUTH_LIBS_DIR/web-component/dist" "$HOT_DIR/fAIr/frontend/auth-libs/web-component/"
cp -r "$AUTH_LIBS_DIR/web-component/src" "$HOT_DIR/fAIr/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/package.json" "$HOT_DIR/fAIr/frontend/auth-libs/web-component/"
cp "$AUTH_LIBS_DIR/web-component/vite.config.js" "$HOT_DIR/fAIr/frontend/auth-libs/web-component/"
echo "✅ Web component (source + dist) → fAIr"
echo ""

# Distribute Python package to fAIr
echo "📦 Distributing Python dist/ to fAIr..."
mkdir -p "$HOT_DIR/fAIr/backend/auth-libs"
rm -rf "$HOT_DIR/fAIr/backend/auth-libs/dist"
cp -r "$AUTH_LIBS_DIR/python/dist" "$HOT_DIR/fAIr/backend/auth-libs/"
echo "✅ Python package → fAIr"
echo ""

echo "✅ Distribution complete!"
echo ""

# Update pyproject.toml references in all projects
echo "📝 Updating pyproject.toml references to v$VERSION..."

update_pyproject() {
    local file="$1"
    if [ -f "$file" ]; then
        # Replace any @vX.X.X or @main with the current version
        sed -i "s|hot-auth-libs.git@[^#]*#|hot-auth-libs.git@v$VERSION#|g" "$file"
        echo "  ✅ Updated: $file"
    fi
}

update_pyproject "$HOT_DIR/portal/backend/pyproject.toml"
update_pyproject "$HOT_DIR/drone-tm/src/backend/pyproject.toml"
update_pyproject "$HOT_DIR/login/backend/pyproject.toml"
update_pyproject "$HOT_DIR/fAIr/backend/pyproject.toml"
update_pyproject "$HOT_DIR/openaerialmap/backend/stac-api/pyproject.toml"

echo ""
echo "✅ All pyproject.toml references updated to v$VERSION"
echo ""
echo "Don't forget to commit changes in each project!"
echo ""
echo "Projects updated:"
echo "  - portal/frontend/auth-libs/web-component/dist/"
echo "  - portal/backend/auth-libs/python/dist/"
echo "  - portal/backend/pyproject.toml → v$VERSION"
echo "  - drone-tm/src/frontend/auth-libs/web-component/dist/"
echo "  - drone-tm/src/backend/auth-libs/dist/"
echo "  - drone-tm/src/backend/pyproject.toml → v$VERSION"
echo "  - login/backend/auth-libs/python/dist/"
echo "  - login/frontend/auth-libs/web-component/dist/"
echo "  - login/backend/pyproject.toml → v$VERSION"
echo "  - openaerialmap/frontend/auth-libs/web-component/dist/"
echo "  - openaerialmap/backend/stac-api/auth-libs/dist/"
echo "  - openaerialmap/backend/stac-api/pyproject.toml → v$VERSION"
echo "  - fAIr/frontend/auth-libs/web-component/dist/"
echo "  - fAIr/backend/auth-libs/dist/"
echo "  - fAIr/backend/pyproject.toml → v$VERSION"
