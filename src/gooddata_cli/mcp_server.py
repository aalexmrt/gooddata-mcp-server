#!/usr/bin/env python3
"""MCP Server for GoodData SDK CLI.

This exposes GoodData operations as MCP tools for use with Claude Code.
All operations are READ-ONLY.
"""

import json
import os
import sys
from pathlib import Path

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("gooddata")


def _load_env():
    """Load environment variables from .env file."""
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()


def _get_sdk():
    """Get GoodData SDK instance."""
    _load_env()
    from gooddata_sdk import GoodDataSdk

    host = os.getenv("GOODDATA_HOST")
    token = os.getenv("GOODDATA_TOKEN")

    if not host or not token:
        raise ValueError("GOODDATA_HOST and GOODDATA_TOKEN must be set")

    return GoodDataSdk.create(host, token)


def _get_workspace_id(workspace_id: str | None = None) -> str:
    """Get workspace ID from argument or environment."""
    if workspace_id:
        return workspace_id

    _load_env()
    env_workspace = os.getenv("GOODDATA_WORKSPACE")

    if not env_workspace:
        raise ValueError("No workspace_id provided and GOODDATA_WORKSPACE not set")

    return env_workspace


# =============================================================================
# LIST TOOLS (Read-Only)
# =============================================================================

@mcp.tool()
def list_workspaces() -> str:
    """List all available GoodData workspaces.

    Returns a JSON array of workspaces with their IDs and names.
    """
    sdk = _get_sdk()
    workspaces = sdk.catalog_workspace.list_workspaces()

    result = [{"id": ws.id, "name": ws.name} for ws in workspaces]
    return json.dumps(result, indent=2)


@mcp.tool()
def list_insights(workspace_id: str | None = None) -> str:
    """List all insights (visualizations) in a workspace.

    Args:
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.

    Returns a JSON array of insights with their IDs and titles.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    am = sdk.catalog_workspace_content.get_declarative_analytics_model(ws_id)

    result = [
        {"id": viz.id, "title": viz.title}
        for viz in am.analytics.visualization_objects
    ]
    return json.dumps(result, indent=2)


@mcp.tool()
def list_dashboards(workspace_id: str | None = None) -> str:
    """List all dashboards in a workspace.

    Args:
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.

    Returns a JSON array of dashboards with their IDs and titles.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    am = sdk.catalog_workspace_content.get_declarative_analytics_model(ws_id)

    result = [
        {"id": db.id, "title": db.title}
        for db in am.analytics.analytical_dashboards
    ]
    return json.dumps(result, indent=2)


@mcp.tool()
def list_metrics(workspace_id: str | None = None) -> str:
    """List all metrics in a workspace.

    Args:
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.

    Returns a JSON array of metrics with their IDs, titles, and formats.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    catalog = sdk.catalog_workspace_content.get_full_catalog(ws_id)

    result = [
        {"id": m.id, "title": m.title, "format": getattr(m, "format", None)}
        for m in catalog.metrics
    ]
    return json.dumps(result, indent=2)


@mcp.tool()
def list_datasets(workspace_id: str | None = None) -> str:
    """List all datasets in a workspace.

    Args:
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.

    Returns a JSON array of datasets with their IDs and titles.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    catalog = sdk.catalog_workspace_content.get_full_catalog(ws_id)

    result = [{"id": ds.id, "title": ds.title} for ds in catalog.datasets]
    return json.dumps(result, indent=2)


# =============================================================================
# USER & GROUP TOOLS (Read-Only)
# =============================================================================

@mcp.tool()
def list_users() -> str:
    """List all users in the GoodData organization.

    Returns a JSON array of users with their IDs and names.
    """
    sdk = _get_sdk()
    users = sdk.catalog_user.list_users()

    result = [
        {
            "id": u.id,
            "name": getattr(u, "name", None),
            "email": getattr(u, "email", None),
        }
        for u in users
    ]
    return json.dumps(result, indent=2)


@mcp.tool()
def list_user_groups() -> str:
    """List all user groups in the GoodData organization.

    Returns a JSON array of groups with their IDs and names.
    """
    sdk = _get_sdk()
    groups = sdk.catalog_user.list_user_groups()

    result = [
        {"id": g.id, "name": getattr(g, "name", None)}
        for g in groups
    ]
    return json.dumps(result, indent=2)


@mcp.tool()
def get_user_group_members(group_id: str) -> str:
    """Get all members of a specific user group.

    Args:
        group_id: The user group ID.

    Returns a JSON array of user IDs in the group.
    """
    sdk = _get_sdk()
    decl_users = sdk.catalog_user.get_declarative_users()

    members = []
    for u in decl_users.users:
        if u.user_groups:
            for ug in u.user_groups:
                if ug.id == group_id:
                    members.append(u.id)
                    break

    return json.dumps({"group_id": group_id, "members": members}, indent=2)


# =============================================================================
# QUERY TOOLS (Read-Only)
# =============================================================================

@mcp.tool()
def get_insight_data(insight_id: str, workspace_id: str | None = None) -> str:
    """Get data from a specific insight/visualization.

    Args:
        insight_id: The insight ID to query.
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.

    Returns the insight data as JSON.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    insight = sdk.insights.get_insight(ws_id, insight_id)
    result = sdk.compute.for_insight(ws_id, insight)

    return json.dumps({
        "headers": [h.header_value for h in result.headers],
        "data": result.data,
    }, indent=2, default=str)


@mcp.tool()
def ai_chat(question: str, workspace_id: str | None = None) -> str:
    """Ask a natural language question about your GoodData data.

    Uses GoodData's AI to answer questions about metrics, trends, etc.

    Args:
        question: The natural language question to ask.
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.

    Returns the AI's response.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    response = sdk.compute.ai_chat(ws_id, question)
    return response.text_response


# =============================================================================
# EXPORT TOOLS (Read-Only - exports to local files)
# =============================================================================

@mcp.tool()
def export_dashboard_pdf(
    dashboard_id: str,
    workspace_id: str | None = None,
    output_path: str | None = None,
) -> str:
    """Export a dashboard to PDF.

    Args:
        dashboard_id: The dashboard ID to export.
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.
        output_path: Optional output file path. Defaults to ./exports/<dashboard_id>.pdf

    Returns the path to the exported file.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    if output_path is None:
        output_dir = Path("exports")
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / f"{dashboard_id}.pdf")

    sdk.export.export_pdf(
        workspace_id=ws_id,
        dashboard_id=dashboard_id,
        file_name=output_path,
    )

    return json.dumps({
        "success": True,
        "path": os.path.abspath(output_path),
    })


@mcp.tool()
def export_visualization_csv(
    visualization_id: str,
    workspace_id: str | None = None,
    output_path: str | None = None,
) -> str:
    """Export a visualization to CSV.

    Args:
        visualization_id: The visualization ID to export.
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.
        output_path: Optional output file path. Defaults to ./exports/<visualization_id>.csv

    Returns the path to the exported file.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    if output_path is None:
        output_dir = Path("exports")
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / f"{visualization_id}.csv")

    sdk.export.export_tabular_by_visualization_id(
        workspace_id=ws_id,
        visualization_id=visualization_id,
        file_name=output_path,
        file_format="CSV",
    )

    return json.dumps({
        "success": True,
        "path": os.path.abspath(output_path),
    })


@mcp.tool()
def export_visualization_xlsx(
    visualization_id: str,
    workspace_id: str | None = None,
    output_path: str | None = None,
) -> str:
    """Export a visualization to Excel (XLSX).

    Args:
        visualization_id: The visualization ID to export.
        workspace_id: The workspace ID. Uses GOODDATA_WORKSPACE env var if not provided.
        output_path: Optional output file path. Defaults to ./exports/<visualization_id>.xlsx

    Returns the path to the exported file.
    """
    sdk = _get_sdk()
    ws_id = _get_workspace_id(workspace_id)

    if output_path is None:
        output_dir = Path("exports")
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / f"{visualization_id}.xlsx")

    sdk.export.export_tabular_by_visualization_id(
        workspace_id=ws_id,
        visualization_id=visualization_id,
        file_name=output_path,
        file_format="XLSX",
    )

    return json.dumps({
        "success": True,
        "path": os.path.abspath(output_path),
    })


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    mcp.run()
