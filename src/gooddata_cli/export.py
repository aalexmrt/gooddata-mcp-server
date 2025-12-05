"""Export operations for GoodData dashboards and visualizations."""

import os
from pathlib import Path
from typing import Literal

from gooddata_cli.sdk import get_sdk, get_workspace_id


def export_dashboard_pdf(
    dashboard_id: str,
    workspace_id: str | None = None,
    output_path: str | None = None,
) -> str:
    """Export a dashboard to PDF.

    Args:
        dashboard_id: The dashboard ID to export.
        workspace_id: Optional workspace ID override.
        output_path: Optional output file path. Defaults to ./exports/<dashboard_id>.pdf

    Returns:
        Path to the exported file.
    """
    sdk = get_sdk()
    ws_id = get_workspace_id(workspace_id)

    if output_path is None:
        output_dir = Path("exports")
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / f"{dashboard_id}.pdf")

    sdk.export.export_pdf(
        workspace_id=ws_id,
        dashboard_id=dashboard_id,
        file_name=output_path,
    )

    return os.path.abspath(output_path)


def export_visualization_tabular(
    visualization_id: str,
    workspace_id: str | None = None,
    output_path: str | None = None,
    format: Literal["CSV", "XLSX"] = "CSV",
) -> str:
    """Export a visualization to CSV or Excel.

    Args:
        visualization_id: The visualization ID to export.
        workspace_id: Optional workspace ID override.
        output_path: Optional output file path.
        format: Export format (CSV or XLSX).

    Returns:
        Path to the exported file.
    """
    sdk = get_sdk()
    ws_id = get_workspace_id(workspace_id)

    extension = format.lower()
    if output_path is None:
        output_dir = Path("exports")
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / f"{visualization_id}.{extension}")

    sdk.export.export_tabular_by_visualization_id(
        workspace_id=ws_id,
        visualization_id=visualization_id,
        file_name=output_path,
        file_format=format,
    )

    return os.path.abspath(output_path)


def export_insight_to_dataframe(
    insight_id: str,
    workspace_id: str | None = None,
):
    """Export an insight's data to a pandas DataFrame.

    Args:
        insight_id: The insight ID to export.
        workspace_id: Optional workspace ID override.

    Returns:
        pandas DataFrame with the insight data.
    """
    from gooddata_pandas import GoodPandas

    sdk = get_sdk()
    ws_id = get_workspace_id(workspace_id)

    gp = GoodPandas(sdk.client.endpoint, sdk.client.token)
    return gp.data_frames(ws_id).for_insight(insight_id)
