# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Main entry point for the Airbyte Manifest Server server."""

import uvicorn


def run_server(
    host: str = "127.0.0.1", port: int = 8000, reload: bool = False, log_level: str = "info"
) -> None:
    """Run the FastAPI server."""

    print(f"🚀 Starting Airbyte CDK Manifest Server on {host}:{port}")

    uvicorn.run(
        "airbyte_cdk.manifest_server.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    run_server()
