# CI/CD Setup Guide

This guide will help you complete the setup of the CI/CD pipeline for the YouTube Downloader project.

## Quick Start

All workflow files are ready to use! Follow these steps to enable full CI/CD functionality:

### 1. Enable GitHub Actions (Automatic)

GitHub Actions will automatically run when you:
- Push code to main/master/develop branches
- Create a pull request
- Push a version tag (e.g., v1.0.1)

### 2. Set Up Codecov (Optional but Recommended)

1. Visit https://codecov.io/
2. Sign in with your GitHub account
3. Add your repository: `JarrydGordon/youtube-downloader`
4. Copy the upload token
5. Add to GitHub repository secrets:
   - Go to: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: [paste your Codecov token]

### 3. Set Up PyPI Publishing (For Releases)

#### Option A: Trusted Publishers (Recommended - No Token Required)

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `youtube-downloader`
   - **Owner**: `JarrydGordon`
   - **Repository name**: `youtube-downloader`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`
4. Click "Add"

That's it! No secrets needed.

#### Option B: API Token (Alternative)

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with scope for `youtube-downloader`
3. Add to GitHub repository secrets:
   - Name: `PYPI_API_TOKEN`
   - Value: [paste your PyPI token]
4. Update `release.yml` to use the token instead of OIDC

### 4. Create Protected Environment (Recommended)

1. Go to: Settings → Environments
2. Click "New environment"
3. Name: `pypi`
4. Configure protection rules:
   - ✅ Required reviewers (select yourself or team)
   - ✅ Wait timer: 5 minutes (optional safety delay)
   - 🔒 Deployment branches: Only protected branches

### 5. Add Status Badges to README

Add these badges to your README.md:

```markdown
[![CI](https://github.com/JarrydGordon/youtube-downloader/workflows/CI/badge.svg)](https://github.com/JarrydGordon/youtube-downloader/actions/workflows/ci.yml)
[![Release](https://github.com/JarrydGordon/youtube-downloader/workflows/Release/badge.svg)](https://github.com/JarrydGordon/youtube-downloader/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/JarrydGordon/youtube-downloader/branch/main/graph/badge.svg)](https://codecov.io/gh/JarrydGordon/youtube-downloader)
[![PyPI version](https://badge.fury.io/py/youtube-downloader.svg)](https://badge.fury.io/py/youtube-downloader)
[![Python versions](https://img.shields.io/pypi/pyversions/youtube-downloader.svg)](https://pypi.org/project/youtube-downloader/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

## Testing the Setup

### Test CI Workflow Locally

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all checks
black --check .
isort --check-only .
flake8 .
mypy youtube_downloader/
bandit -r youtube_downloader/
pytest --cov=youtube_downloader

# Auto-fix formatting issues
black .
isort .
```

### Test Release Workflow

1. **Test on Test PyPI first:**
   ```bash
   # Create a test version tag
   git tag v1.0.0-test
   git push origin v1.0.0-test
   
   # Manually trigger workflow with workflow_dispatch
   # Go to Actions → Release → Run workflow
   ```

2. **Create a real release:**
   ```bash
   # Update version in setup.py and pyproject.toml
   # Commit changes
   git add setup.py pyproject.toml
   git commit -m "chore: bump version to 1.0.1"
   
   # Create and push tag
   git tag v1.0.1
   git push origin v1.0.1
   
   # Watch the release workflow in Actions tab
   ```

## Workflow Files Overview

| File | Purpose | Triggers |
|------|---------|----------|
| `ci.yml` | Run tests, linting, type checking | Push, PR |
| `release.yml` | Build and publish to PyPI | Tag push (v*.*.*) |
| `dependabot.yml` | Auto-update dependencies | Weekly |

## CI Workflow Matrix

The CI runs on:
- **Python versions**: 3.9, 3.10, 3.11, 3.12
- **Operating systems**: Ubuntu, Windows, macOS
- **Total jobs**: 12 test jobs + 2 quality jobs + 1 summary

## Troubleshooting

### CI Failing on First Run

This is normal! The workflows might fail initially because:

1. **Missing dependencies**: Make sure all dependencies are in `requirements.txt`
2. **Code formatting**: Run `black .` and `isort .` locally first
3. **Type errors**: Fix any mypy errors or add `# type: ignore` comments
4. **Test failures**: Ensure all tests pass locally first

### Release Workflow Issues

**Problem**: PyPI publish fails with "403 Forbidden"
- **Solution**: Verify Trusted Publisher setup or API token

**Problem**: Tag doesn't trigger workflow
- **Solution**: Ensure tag format is `v*.*.*` (e.g., v1.0.0, not 1.0.0)

**Problem**: Version already exists on PyPI
- **Solution**: Update version number in `setup.py` and `pyproject.toml`

### Codecov Upload Fails

**Problem**: "Codecov token not found"
- **Solution**: Add `CODECOV_TOKEN` to repository secrets

**Problem**: Coverage report not showing
- **Solution**: Wait a few minutes, Codecov processing takes time

## Maintenance

### Update Dependencies

Dependabot will automatically create PRs for:
- GitHub Actions version updates (weekly)
- Python package updates (weekly)

Review and merge these PRs to keep dependencies current.

### Monitor Workflow Runs

- View at: https://github.com/JarrydGordon/youtube-downloader/actions
- Set up notifications: Settings → Notifications → Actions

### Adjust Python Versions

Edit the matrix in `ci.yml` and `release.yml`:

```yaml
matrix:
  python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']  # Add 3.13
```

## Best Practices

1. ✅ **Always run checks locally before pushing**
2. ✅ **Keep dependencies up to date** (review Dependabot PRs)
3. ✅ **Monitor CI status** (don't merge failing PRs)
4. ✅ **Write tests for new features**
5. ✅ **Update version numbers before tagging**
6. ✅ **Review release notes before publishing**

## Getting Help

- **GitHub Actions docs**: https://docs.github.com/en/actions
- **PyPI Trusted Publishers**: https://docs.pypi.org/trusted-publishers/
- **Codecov docs**: https://docs.codecov.com/

## Next Steps

1. ✅ Commit all new files
2. ✅ Push to GitHub
3. ✅ Watch the CI workflow run
4. ✅ Set up Codecov (optional)
5. ✅ Configure PyPI Trusted Publisher
6. ✅ Add badges to README
7. ✅ Create your first release!

---

**Everything is ready to go! Your CI/CD pipeline follows 2025 best practices.**
