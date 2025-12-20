# Contributing to GoodData MCP Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- A GoodData account with API access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aalexmrt/gooddata-mcp-server.git
   cd gooddata-mcp-server
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev,mcp]"
   ```

4. Set up your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your GoodData credentials
   ```

## Code Style

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Guidelines

- Keep functions focused and single-purpose
- Add docstrings to all public functions
- Use type hints for function parameters and return values
- Follow the existing code patterns in the project

## Making Changes

### Branching

1. Create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with clear, focused commits

3. Push your branch and open a Pull Request

### Commit Messages

Write clear, concise commit messages:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 72 characters

Examples:
- `Add workspace filtering to list_insights tool`
- `Fix error handling in export_dashboard_pdf`
- `Update README with new installation instructions`

## Pull Requests

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what changes you made and why
3. **Testing**: Describe how you tested your changes
4. **Breaking changes**: Note any breaking changes

### PR Checklist

- [ ] Code follows the project style guidelines
- [ ] Self-reviewed the code
- [ ] Added/updated docstrings for new/changed functions
- [ ] Tested changes locally with a real GoodData instance
- [ ] Updated README if adding new features

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the problem
2. **Steps to reproduce**: How to trigger the issue
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Python version, OS, GoodData SDK version

## Adding New MCP Tools

When adding new tools to the MCP server:

1. Add the function in `src/gooddata_cli/mcp_server.py`
2. Use the `@mcp.tool()` decorator
3. Include a comprehensive docstring (this becomes the tool description)
4. Keep operations **read-only** (this is a design principle of this project)
5. Handle errors gracefully and return meaningful error messages
6. Update the README's tool table

Example:
```python
@mcp.tool()
def my_new_tool(workspace_id: str | None = None) -> str:
    """Short description of what the tool does.

    Longer description with details about the tool's behavior.

    Args:
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.

    Returns:
        JSON string with the results.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    # Implementation
    result = {"key": "value"}
    return json.dumps(result, indent=2)
```

## Questions?

If you have questions, feel free to open an issue with the "question" label.

Thank you for contributing!
