# Contributing to Bore Interactive Inputs

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- GitHub account
- Basic understanding of GitHub Actions

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/bore-interactive-inputs.git
   cd bore-interactive-inputs
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
bore-interactive-inputs/
├── .github/
│   └── workflows/
│       └── test.yml          # Test workflow
├── src/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Main entry point
│   ├── server.py             # Flask web server
│   ├── bore_tunnel.py        # Bore tunnel management
│   ├── config.py             # Configuration handling
│   └── notifiers.py          # Slack/Discord notifications
├── action.yml                # GitHub Action definition
├── README.md                 # Main documentation
├── SETUP.md                  # Setup guide
├── LICENSE                   # MIT License
└── requirements.txt          # Python dependencies
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Follow PEP 8 style guidelines for Python code
- Add comments for complex logic
- Update documentation if needed

### 3. Test Your Changes

Test locally by creating a test workflow in your fork:

```yaml
name: Test My Changes

on:
  push:
    branches: [feature/your-feature-name]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./
        with:
          bore-server: 'bore.pub'
          interactive: |
            fields:
              - label: test
                properties:
                  type: text
```

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add support for custom file upload directory"
```

Follow this format:
- `feat: Add new feature`
- `fix: Fix bug in bore tunnel`
- `docs: Update README`
- `refactor: Improve code structure`
- `test: Add test workflow`

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Why the changes are needed
- How to test the changes
- Screenshots (if applicable)

## Code Style

### Python

- Follow PEP 8
- Use type hints where applicable
- Maximum line length: 100 characters
- Use docstrings for functions and classes

Example:
```python
def process_field(field: Dict[str, Any], value: Any) -> str:
    """
    Process a field value based on its type.
    
    Args:
        field: Field configuration dictionary
        value: The field value to process
    
    Returns:
        Processed value as string
    """
    # Implementation here
    pass
```

### YAML

- Use 2 spaces for indentation
- Keep lines under 100 characters
- Add comments for complex configurations

## Adding New Features

### Adding a New Field Type

1. Update `server.py` to handle the new field type in `renderField()` function
2. Update `server.py` to process the field in `_process_submission()` method
3. Add example to README.md
4. Add test case in `.github/workflows/test.yml`

Example for adding a "color" field type:

```python
# In server.py - renderField()
elif type == 'color':
    return f'<input type="color" name="{label}" id="{label}" value="{defaultValue}">'

# In server.py - _process_submission()
# Color type returns as-is (string)
```

### Adding a New Notifier

1. Create a new class in `notifiers.py` that extends `Notifier`
2. Implement the `send()` method
3. Update `config.py` to add configuration options
4. Update `main.py` to instantiate the notifier
5. Update `action.yml` to add inputs
6. Document in README.md and SETUP.md

Example:

```python
# In notifiers.py
class TeamsNotifier(Notifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, status: str, message: str, url: Optional[str] = None,
             workflow: str = '', repository: str = '', run_id: str = ''):
        # Implementation here
        pass
```

## Testing

### Manual Testing

1. Create a test repository with your changes
2. Create a workflow that uses the action
3. Trigger the workflow and test all field types
4. Verify outputs are correct
5. Test with different configurations

### Testing Checklist

- [ ] All field types work correctly
- [ ] File uploads work and are accessible
- [ ] Outputs are correctly set
- [ ] Notifications work (if enabled)
- [ ] Bore tunnel establishes correctly
- [ ] Timeout handling works
- [ ] Error messages are helpful

## Documentation

When making changes, update relevant documentation:

- **README.md**: Feature descriptions, examples, API reference
- **SETUP.md**: Setup instructions, configuration details
- **Code comments**: Inline documentation for complex logic

## Questions?

If you have questions:

1. Check existing documentation (README, SETUP)
2. Search closed issues
3. Create a new issue with the "question" label

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)

Thank you for contributing! 🎉
