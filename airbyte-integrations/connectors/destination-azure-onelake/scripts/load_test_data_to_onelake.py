#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

from azure.identity import ClientSecretCredential
from azure.storage.blob import ContainerClient


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "sample_secrets" / "config.json"


def load_config(path: Path) -> dict:
    with path.open("r") as f:
        return json.load(f)


def main() -> None:
    config = load_config(CONFIG_PATH)

    workspace = config["azure_blob_storage_account_name"].strip()
    lakehouse_raw = config["azure_blob_storage_container_name"].strip()
    tenant_id = config["azure_tenant_id"].strip()
    client_id = config["azure_client_id"].strip()
    client_secret = config["azure_client_secret"].strip()

    # OneLake: container = workspace, path = item.itemtype/Files/...
    container_name = workspace
    item_path = f"{lakehouse_raw}.Lakehouse" if "." not in lakehouse_raw else lakehouse_raw

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    blob_name = f"{item_path}/Files/airbyte/test_data/test_data_{ts}.jsonl"

    records = [
        {
            "source": "test-script",
            "order_id": f"TEST-{i}",
            "amount": 10.5 * i,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        for i in range(1, 6)
    ]
    body = "\n".join(json.dumps(r) for r in records) + "\n"

    endpoint = "https://onelake.blob.fabric.microsoft.com"
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # Older azure-storage-blob uses ContainerClient instead of service_client.get_blob_container_client
    container = ContainerClient(account_url=endpoint, credential=credential, container_name=container_name)
    blob = container.get_blob_client(blob_name)

    print("Uploading test data to OneLake...")
    print(f"  container: {container_name}")
    print(f"  blob:      {blob_name}")

    blob.upload_blob(body.encode("utf-8"), overwrite=True)

    print("Upload completed.")


if __name__ == "__main__":
    main()

