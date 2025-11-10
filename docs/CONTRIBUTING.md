# Contributing to YouTube Downloader

Thank you for your interest in contributing to YouTube Downloader! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- FFmpeg (for video/audio processing)

### Getting Started

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. **Install the package in editable mode**

```bash
pip install -e .
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=youtube_downloader --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run tests in parallel
pytest -n auto
```

### Code Quality Checks

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Check code style with flake8
flake8 .

# Type checking with mypy
mypy youtube_downloader/

# Security scanning with bandit
bandit -r youtube_downloader/
```

### Pre-commit Checks

Before committing, ensure all checks pass:

```bash
# Run all quality checks
black --check .
isort --check-only .
flake8 .
mypy youtube_downloader/
pytest
```

## Coding Standards

### Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Maximum line length: 100 characters
- Use Black for code formatting
- Use isort for import sorting
- Add type hints where possible

### Documentation

- Write docstrings for all public modules, functions, classes, and methods
- Use Google-style docstrings
- Keep documentation up-to-date with code changes
- Add comments for complex logic

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

## Pull Request Process

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write clean, maintainable code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**

```bash
black .
isort .
flake8 .
mypy youtube_downloader/
pytest
```

4. **Commit your changes**

```bash
git add .
git commit -m "feat: add your feature description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

5. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

6. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure all CI checks pass

## CI/CD Pipeline

Our project uses GitHub Actions for continuous integration and deployment:

### CI Pipeline (on push/PR)
- ✅ Code quality checks (Black, isort, Flake8)
- ✅ Type checking (mypy)
- ✅ Security scanning (Bandit)
- ✅ Tests on Python 3.9, 3.10, 3.11, 3.12
- ✅ Tests on Ubuntu, Windows, macOS
- ✅ Coverage reporting to Codecov

### Release Pipeline (on tag push)
- 📦 Build wheel and source distributions
- 🧪 Test distributions on multiple platforms
- 🚀 Publish to PyPI
- 📝 Create GitHub release with changelog

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
