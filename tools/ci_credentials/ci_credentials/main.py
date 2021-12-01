import json
import os
import sys
from json.decoder import JSONDecodeError

from ci_common_utils import Logger
from credentials_loader import CredentialsLoader

logger = Logger()


# credentials of GSM and GitHub secrets should be shared via shell environment

def main() -> int:
    if len(sys.argv) != 2:
        return logger.error("uses one script argument only: <unique connector name>")

    # parse unique connector name, because it can have the common prefix "connectors/<unique connector name>"
    connector_name = sys.argv[1].split("/")[-1]
    if connector_name == "all":
        # if needed to load all secrets
        connector_name = None
        
    # parse GITHUB_PROVIDED_SECRETS_JSON
    try:
        github_secrets = json.loads(os.getenv("GITHUB_PROVIDED_SECRETS_JSON") or "{}")
    except JSONDecodeError as e:
        return logger.error(f"incorrect GITHUB_PROVIDED_SECRETS_JSON value, error: {e}")

    # parse GCP_GSM_CREDENTIALS
    try:
        gsm_credentials = json.loads(os.getenv("GCP_GSM_CREDENTIALS") or "{}")
    except JSONDecodeError as e:
        return logger.error(f"incorrect GCP_GSM_CREDENTIALS value, error: {e}")
    if not gsm_credentials:
        return logger.error(f"GCP_GSM_CREDENTIALS shouldn't be empty!")

    loader = CredentialsLoader(
        connector_name=connector_name,
        gsm_credentials=gsm_credentials,
        github_secrets=github_secrets
    )
    return loader.read() or loader.write()


if __name__ == '__main__':
    sys.exit(main())
