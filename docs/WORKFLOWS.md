# GitHub Actions Workflows

This directory contains the CI/CD workflows for the YouTube Downloader project.

## Workflows

### 1. CI Workflow (`ci.yml`)

**Trigger:** Push to main/master/develop branches, Pull Requests

**Jobs:**

#### Code Quality Checks
- **Black**: Code formatting verification
- **isort**: Import sorting verification
- **Flake8**: Linting and style checks
- **Bandit**: Security vulnerability scanning
- **Timeout**: 10 minutes
- **Artifacts**: Bandit security report (30-day retention)

#### Type Checking
- **mypy**: Static type checking
- **Python Version**: 3.12
- **Timeout**: 10 minutes

#### Test Matrix
- **Python Versions**: 3.9, 3.10, 3.11, 3.12
- **Operating Systems**: Ubuntu, Windows, macOS
- **Total Combinations**: 12 (4 Python × 3 OS)
- **Test Framework**: pytest
- **Coverage**: pytest-cov with HTML, XML, and terminal reports
- **Timeout**: 15 minutes per job
- **Artifacts**:
  - Test results (JUnit XML)
  - Coverage reports (HTML)
  - Coverage data (XML for Codecov)
- **Codecov Integration**: Ubuntu-only uploads with per-Python-version flags

#### Test Summary
- Validates all previous jobs
- Provides consolidated status
- Fails if any critical checks fail

**Features:**
- ✅ Pip caching for faster runs
- ✅ Parallel execution (up to 12 jobs)
- ✅ Concurrency control (cancels outdated runs)
- ✅ Artifact uploads with 30-day retention
- ✅ Codecov integration for coverage tracking

### 2. Release Workflow (`release.yml`)

**Trigger:** 
- Tag push (v*.*.*)
- Manual workflow dispatch

**Jobs:**

#### Build Distributions
- **Python Version**: 3.12
- **Outputs**: Wheel (.whl) and source (.tar.gz) distributions
- **Validation**: twine check
- **Timeout**: 10 minutes
- **Artifacts**: Distributions (90-day retention)

#### Test Distributions
- **Matrix**: Ubuntu, Windows, macOS × Python 3.9, 3.12
- **Tests**: Installation verification and import checks
- **Timeout**: 10 minutes per job

#### Publish to PyPI
- **Requirement**: Build and test jobs must succeed
- **Method**: Trusted Publisher (OIDC, no API token required)
- **Environment**: pypi (with protection rules)
- **Timeout**: 10 minutes

#### GitHub Release
- **Auto-generated changelog** from git commits
- **Release assets**: Wheel and source distributions
- **Prerelease detection**: Alpha, beta, RC versions
- **Timeout**: 10 minutes

#### Publish to Test PyPI (Optional)
- **Trigger**: Manual workflow dispatch only
- **Purpose**: Test release process without affecting production
- **Environment**: test-pypi

**Features:**
- ✅ Multi-platform distribution testing
- ✅ Trusted Publishers (OIDC) for PyPI
- ✅ Automatic changelog generation
- ✅ Asset upload to GitHub releases
- ✅ Prerelease detection
- ✅ Test PyPI option for dry runs

## Permissions

### CI Workflow
- **Default**: Read access to repository
- **Contents**: Read (checkout code)
- **Checks**: Write (publish test results)

### Release Workflow
- **Contents**: Write (create releases)
- **id-token**: Write (OIDC for PyPI Trusted Publishers)

## Secrets Required

### For CI
- `CODECOV_TOKEN` (optional): For uploading coverage to Codecov
  - Get from: https://codecov.io/

### For Release
- **PyPI**: No secrets required (uses Trusted Publishers)
  - Set up at: https://pypi.org/manage/account/publishing/
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

## Setting Up PyPI Trusted Publishers

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - **Repository**: JarrydGordon/youtube-downloader
   - **Workflow**: release.yml
   - **Environment**: pypi
3. No API tokens needed!

## Caching Strategy

All workflows use pip caching:
```yaml
- uses: actions/setup-python@v5
  with:
    cache: 'pip'
    cache-dependency-path: |
      requirements.txt
      requirements-dev.txt
```

**Benefits:**
- ⚡ Faster workflow execution (30-60% time reduction)
- 💰 Reduced bandwidth usage
- 🔄 Automatic cache invalidation on dependency changes

## Workflow Optimization

### Concurrency Control
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
- Cancels outdated workflow runs on new commits
- Saves CI minutes and resources

### Timeout Limits
- Code quality: 10 minutes
- Type checking: 10 minutes
- Tests: 15 minutes per job
- Release jobs: 10 minutes each

### Fail-Fast Strategy
```yaml
strategy:
  fail-fast: false
```
- Tests run across all combinations even if one fails
- Provides complete picture of compatibility

## Monitoring and Debugging

### View Workflow Runs
- Go to: https://github.com/JarrydGordon/youtube-downloader/actions

### Debug Failed Runs
1. Check the job logs for error details
2. Download artifacts (test results, coverage reports)
3. Review Codecov reports for coverage changes
4. Check Bandit reports for security issues

### Local Testing
Run the same checks locally before pushing:
```bash
# Code quality
black --check .
isort --check-only .
flake8 .

# Type checking
mypy youtube_downloader/

# Security
bandit -r youtube_downloader/

# Tests
pytest --cov=youtube_downloader
```

## Badge URLs

Add these to your README.md:

```markdown
![CI](https://github.com/JarrydGordon/youtube-downloader/workflows/CI/badge.svg)
![Release](https://github.com/JarrydGordon/youtube-downloader/workflows/Release/badge.svg)
[![codecov](https://codecov.io/gh/JarrydGordon/youtube-downloader/branch/main/graph/badge.svg)](https://codecov.io/gh/JarrydGordon/youtube-downloader)
[![PyPI version](https://badge.fury.io/py/youtube-downloader.svg)](https://badge.fury.io/py/youtube-downloader)
[![Python versions](https://img.shields.io/pypi/pyversions/youtube-downloader.svg)](https://pypi.org/project/youtube-downloader/)
```

## Troubleshooting

### Common Issues

**1. pip cache not working**
- Ensure requirements files are committed
- Check cache-dependency-path includes all requirements files

**2. Codecov uploads failing**
- Verify CODECOV_TOKEN is set in repository secrets
- Check if Codecov service is operational

**3. PyPI publish failing**
- Ensure Trusted Publisher is configured correctly
- Verify version number doesn't already exist on PyPI
- Check that version in setup.py matches the tag

**4. Tests failing only in CI**
- Check for environment-specific issues
- Verify all dependencies are in requirements.txt
- Look for hardcoded paths or OS-specific code

## Updates and Maintenance

### Updating Actions Versions

Dependabot can automatically update action versions. Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Monitoring Action Updates
- Watch https://github.com/actions for new releases
- Review changelogs before updating major versions
- Test in separate branch before merging

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [Codecov Documentation](https://docs.codecov.com/)
- [pytest Documentation](https://docs.pytest.org/)
