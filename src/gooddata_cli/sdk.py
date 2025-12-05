"""SDK initialization and configuration."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from gooddata_sdk import GoodDataSdk


def _load_env() -> None:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()


@lru_cache(maxsize=1)
def get_sdk() -> GoodDataSdk:
    """Get a cached GoodData SDK instance.

    Returns:
        GoodDataSdk: Configured SDK instance.

    Raises:
        ValueError: If GOODDATA_HOST or GOODDATA_TOKEN are not set.
    """
    _load_env()

    host = os.getenv("GOODDATA_HOST")
    token = os.getenv("GOODDATA_TOKEN")

    if not host:
        raise ValueError("GOODDATA_HOST environment variable is not set")
    if not token:
        raise ValueError("GOODDATA_TOKEN environment variable is not set")

    return GoodDataSdk.create(host, token)


def get_workspace_id(workspace_id: str | None = None) -> str:
    """Get workspace ID from argument or environment.

    Args:
        workspace_id: Optional workspace ID override.

    Returns:
        str: The workspace ID to use.

    Raises:
        ValueError: If no workspace ID is provided or configured.
    """
    if workspace_id:
        return workspace_id

    _load_env()
    env_workspace = os.getenv("GOODDATA_WORKSPACE")

    if not env_workspace:
        raise ValueError(
            "No workspace ID provided. Either pass --workspace or set GOODDATA_WORKSPACE"
        )

    return env_workspace
