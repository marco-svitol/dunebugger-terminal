# Versioning System

## Overview

This component uses semantic versioning with automated release management. The version follows the format `MAJOR.MINOR.PATCH` with optional prerelease identifiers (e.g., `beta.5`).

## Version Detection Strategy

The version detection follows a two-tier approach:

1. **Production**: Reads from `VERSION` file (JSON format)
2. **Development**: Falls back to `git describe --tags` 
3. **Fallback**: Returns `0.0.0-unknown` if neither is available

## VERSION File Format

Production deployments include a VERSION file in JSON format:

```json
{
  "version": "1.2.3",
  "build": "release",
  "commit": "abc1234"
}
```

The `build` field can be:
- `release` - Production release
- `beta.N` - Beta prerelease
- `devN` - Development build (N commits since tag)
- `*.dirty` - Uncommitted changes

## Automated Releases

Releases are automated via GitHub Actions using semantic-release:

### Commit Message Format

Use Conventional Commits format:

- `feat:` - New feature (minor version bump)
- `fix:` - Bug fix (patch version bump)
- `feat!:` or `BREAKING CHANGE:` - Breaking change (major version bump)
- `chore:` - No release

### Branch Strategy

- **main**: Production releases (e.g., `1.2.3`)
- **develop**: Beta prereleases (e.g., `1.3.0-beta.1`)

### Release Artifacts

Each release generates:
- `dunebugger-terminal-{version}.tar.gz` - Deployment artifact with VERSION file
- `dunebugger-terminal-{version}.tar.gz.sha256` - Checksum for verification

## Development Workflow

### Local Development

When working locally, the version is detected from git automatically:

```bash
python3 -c "from app.version import get_version_info; import json; print(json.dumps(get_version_info(), indent=2))"
```

### Creating a Release

1. Commit with conventional commit message:
   ```bash
   git commit -m "feat: add new terminal command"
   ```

2. Push to main or develop:
   ```bash
   git push origin develop
   ```

3. GitHub Actions automatically:
   - Determines version bump
   - Creates git tag
   - Generates CHANGELOG.md
   - Creates VERSION file
   - Builds release artifact
   - Publishes to GitHub Releases

## Deployment

### Production Deployment

Download and extract the release artifact:

```bash
# Download artifact from GitHub Releases
wget https://github.com/marco-svitol/dunebugger-terminal/releases/download/v1.2.3/dunebugger-terminal-1.2.3.tar.gz
wget https://github.com/marco-svitol/dunebugger-terminal/releases/download/v1.2.3/dunebugger-terminal-1.2.3.tar.gz.sha256

# Verify checksum
sha256sum -c dunebugger-terminal-1.2.3.tar.gz.sha256

# Extract
tar xzf dunebugger-terminal-1.2.3.tar.gz -C /opt/dunebugger-terminal/

# VERSION file is included - no git needed!
```

The extracted artifact includes the VERSION file, so git is not required in production.

### Updater Integration

Your updater system can:

1. Query GitHub Releases API for latest version
2. Download the artifact
3. Verify SHA256 checksum
4. Extract to deployment location
5. Restart service

No git operations needed on production hosts.

## Version API

The version is accessible via the message queue:

```python
from app.version import get_version_info

version_info = get_version_info()
# {
#   "version": "1.2.3",
#   "build": "release",
#   "commit": "abc1234",
#   "full_version": "1.2.3-release+abc1234"
# }
```

## Manual VERSION File Generation

For testing or special cases:

```bash
./generate_version.sh
```

This creates a VERSION file from current git state.
