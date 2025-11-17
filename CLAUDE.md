# Auth-libs Development Guide

This file provides guidance to Claude Code when working with auth-libs.

## Overview

Auth-libs provides **centralized authentication** for all HOTOSM applications:

- **Hanko SSO**: JWT-based authentication
- **OSM OAuth**: OpenStreetMap account linking
- **User Mapping**: Maps Hanko users to app-specific user IDs

## Structure

```
auth-libs/
├── python/                   # FastAPI integration package
│   ├── hotosm_auth/
│   │   ├── __init__.py
│   │   ├── models/          # SQLAlchemy models
│   │   ├── integrations/    # FastAPI dependencies
│   │   └── utils/           # Helper functions
│   ├── dist/                # Built wheel (generated)
│   └── pyproject.toml
├── web-component/            # Lit web component
│   ├── src/
│   │   └── hanko-auth.ts   # Main component
│   ├── dist/                # Built bundles (generated)
│   └── package.json
└── scripts/
    ├── build.sh             # Builds everything
    └── distribute.sh        # Copies dist/ to projects
```

## Development Workflow

### 1. Make Changes

Edit source code in this repository:
- Python: `python/hotosm_auth/`
- Web component: `web-component/src/`

### 2. Build

```bash
cd /home/willaru/dev/HOT/auth-libs
./scripts/build.sh
```

This creates:
- `python/dist/*.whl` - Python wheel
- `web-component/dist/*.js` - JS bundles

### 3. Distribute

```bash
./scripts/distribute.sh
```

This copies `dist/` folders to:
- `../portal/frontend/auth-libs/web-component/dist/`
- `../portal/backend/auth-libs/python/dist/`
- `../drone-tm/src/backend/auth-libs/dist/`

### 4. Test

Test in the target projects:
```bash
cd ../portal
make dev
# Test authentication flows
```

### 5. Commit

Commit changes in **both** auth-libs and target projects:
```bash
# In auth-libs
git add .
git commit -m "Add user mapping feature"

# In each project
cd ../portal
git add frontend/auth-libs backend/auth-libs
git commit -m "Update auth-libs dist"
```

## Key Features

### Python Package (`hotosm_auth`)

**FastAPI Dependencies:**
- `CurrentUser` - Validates Hanko JWT, returns user
- `OSMConnectionRequired` - Requires OSM OAuth
- `get_mapped_user_id()` - Maps Hanko user to app user

**Usage Example:**
```python
from hotosm_auth.integrations.fastapi import CurrentUser

@router.get("/me")
async def get_me(user: CurrentUser):
    return {"id": user.id, "email": user.email}
```

### Web Component (`hotosm-auth`)

**Attributes:**
- `hanko-url` - Hanko API URL
- `show-profile` - Show profile dropdown
- `osm-required` - Require OSM connection
- `auto-connect` - Auto-redirect to OSM OAuth
- `redirect-after-login` - Where to go after login

**Usage Example:**
```html
<hotosm-auth
  hanko-url="http://localhost:8002"
  osm-required="true"
  auto-connect="true"
  show-profile
/>
```

## Distribution Strategy

**Why copy dist/ instead of npm link or symlinks?**

1. ✅ Works with Docker builds
2. ✅ CI/CD has everything it needs
3. ✅ Each project deployable independently
4. ✅ No runtime dependencies on auth-libs repo

**Future:** When mature, publish to PyPI/npm and use versioned dependencies.

## DO NOT

- ❌ Edit source code directly in project `auth-libs/` directories
- ❌ Edit `dist/` files directly (they're generated)
- ❌ Push dist/ to auth-libs repo (gitignored)

## DO

- ✅ Edit source here
- ✅ Build + distribute after changes
- ✅ Test in projects before committing
- ✅ Commit dist/ in each project
- ✅ Document breaking changes in commit messages

## Git Commit Messages

Keep commit messages simple and human-like:

**DO:**
- ✅ "Fix login redirect bug"
- ✅ "Add OSM logout endpoint"
- ✅ "Update deploy workflow secrets"

**DON'T:**
- ❌ Mention AI/Claude/automation
- ❌ Use robotic language
- ❌ Add unnecessary metadata

Write as if a developer typed it quickly - concise, clear, natural.
