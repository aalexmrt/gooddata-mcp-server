# GoodData SDK CLI

A command-line tool and MCP server for interacting with GoodData via the official Python SDK.

## Important: Read-Only Operations

**All tools in this project are READ-ONLY.** This CLI does not create, update, or delete any data in GoodData. Operations are limited to:
- Listing resources (workspaces, insights, dashboards, metrics, datasets, users, groups)
- Querying existing data
- Exporting reports to local files

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/gooddata-sdk.git
cd gooddata-sdk

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .

# For MCP server support
pip install mcp
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your GoodData credentials:
   ```
   GOODDATA_HOST=https://your-org.cloud.gooddata.com
   GOODDATA_TOKEN=your-api-token
   GOODDATA_WORKSPACE=your-default-workspace-id
   ```

   To get an API token, go to your GoodData profile settings and create a Personal Access Token.

## CLI Usage

### List Resources

```bash
# List all workspaces
gooddata list workspaces

# List insights in a workspace
gooddata list insights -w <workspace_id>

# List dashboards
gooddata list dashboards -w <workspace_id>

# List metrics
gooddata list metrics -w <workspace_id>

# List datasets
gooddata list datasets -w <workspace_id>

# JSON output
gooddata list workspaces --json
```

### Query Data

```bash
# Get data from a specific insight
gooddata insight <insight_id> -w <workspace_id>

# AI-powered natural language query
gooddata chat "What were total sales last month?" -w <workspace_id>

# Reset chat history before asking
gooddata chat "Start fresh question" -w <workspace_id> --reset
```

### Export

```bash
# Export dashboard to PDF
gooddata export pdf <dashboard_id> -w <workspace_id>

# Export visualization to CSV
gooddata export csv <visualization_id> -w <workspace_id>

# Export visualization to Excel
gooddata export xlsx <visualization_id> -w <workspace_id>

# Custom output path
gooddata export pdf <dashboard_id> -o ./my-report.pdf
```

## MCP Server (for Claude Code)

This project includes an MCP server that exposes GoodData tools to Claude Code.

### Setup

```bash
# Register the MCP server with Claude Code
claude mcp add gooddata \
  -s user \
  -e GOODDATA_HOST="https://your-org.cloud.gooddata.com" \
  -e GOODDATA_TOKEN="your-api-token" \
  -e GOODDATA_WORKSPACE="your-workspace-id" \
  -- /path/to/gooddata-sdk/.venv/bin/python -m gooddata_cli.mcp_server
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `list_workspaces` | List all workspaces |
| `list_insights` | List insights in a workspace |
| `list_dashboards` | List dashboards in a workspace |
| `list_metrics` | List metrics in a workspace |
| `list_datasets` | List datasets in a workspace |
| `list_users` | List all users |
| `list_user_groups` | List all user groups |
| `get_user_group_members` | Get members of a group |
| `get_insight_data` | Get data from an insight |
| `ai_chat` | AI-powered natural language query |
| `export_dashboard_pdf` | Export dashboard to PDF |
| `export_visualization_csv` | Export visualization to CSV |
| `export_visualization_xlsx` | Export visualization to Excel |

### Management

```bash
# Check server status
claude mcp list

# Remove the server
claude mcp remove gooddata
```

## Python API

```python
from gooddata_cli.query import list_workspaces, list_insights, ai_chat
from gooddata_cli.export import export_dashboard_pdf, export_visualization_tabular

# List workspaces
workspaces = list_workspaces()

# List insights
insights = list_insights(workspace_id="my_workspace")

# AI chat
response = ai_chat("What is our top selling product?", workspace_id="my_workspace")

# Export dashboard
path = export_dashboard_pdf("dashboard_id", workspace_id="my_workspace")
```

## Project Structure

```
gooddata-sdk/
├── .env.example           # Environment template
├── pyproject.toml         # Package configuration
├── README.md              # This file
├── src/gooddata_cli/
│   ├── __init__.py        # Package exports
│   ├── sdk.py             # SDK initialization
│   ├── query.py           # Query operations
│   ├── export.py          # Export operations
│   ├── cli.py             # CLI entry point
│   └── mcp_server.py      # MCP server for Claude Code
└── scripts/
    └── analyze_permissions.py  # User/group analysis script
```

## Dependencies

- [gooddata-sdk](https://pypi.org/project/gooddata-sdk/) - Official GoodData Python SDK
- [gooddata-pandas](https://pypi.org/project/gooddata-pandas/) - Pandas integration
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Environment variable loading
- [click](https://pypi.org/project/click/) - CLI framework
- [rich](https://pypi.org/project/rich/) - Terminal formatting
- [mcp](https://pypi.org/project/mcp/) - Model Context Protocol (for Claude Code integration)

## License

MIT
