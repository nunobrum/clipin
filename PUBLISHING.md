# Publishing clipin to PyPI

This guide explains how to publish the clipin package to PyPI.

## Prerequisites

1. Create an account on [PyPI](https://pypi.org/account/register/)
2. (Optional) Create an account on [TestPyPI](https://test.pypi.org/account/register/) for testing
3. Install required tools:
   ```bash
   pip install --upgrade pip build twine
   ```

## Build the Package

Build the distribution packages (wheel and source distribution):

```bash
python3 -m build
```

This will create files in the `dist/` directory:
- `clipin-0.1.0-py3-none-any.whl` (wheel)
- `clipin-0.1.0.tar.gz` (source distribution)

## Test on TestPyPI (Recommended)

Before uploading to the real PyPI, test on TestPyPI:

```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ clipin
```

## Upload to PyPI

Once you've verified everything works on TestPyPI:

```bash
python3 -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

## Using API Tokens (Recommended)

For better security, use API tokens instead of passwords:

1. Go to your [PyPI account settings](https://pypi.org/manage/account/)
2. Create an API token
3. Create a `~/.pypirc` file:

```ini
[pypi]
username = __token__
password = pypi-YourTokenHere
```

Then upload with:

```bash
python3 -m twine upload dist/*
```

## Installation

After publishing, users can install your package with:

```bash
pip install clipin
```

## Updating the Package

1. Update the version in `pyproject.toml`
2. Clean old builds: `rm -rf dist/ build/ *.egg-info/`
3. Build new distributions: `python3 -m build`
4. Upload: `python3 -m twine upload dist/*`

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [twine documentation](https://twine.readthedocs.io/)
