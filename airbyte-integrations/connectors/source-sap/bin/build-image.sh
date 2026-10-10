#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

TAG="$(python3 -c "import re,pathlib;print(re.search(r'dockerImageTag: (\S+)', pathlib.Path('metadata.yaml').read_text()).group(1))")"
REPO="$(python3 -c "import re,pathlib;print(re.search(r'dockerRepository: (\S+)', pathlib.Path('metadata.yaml').read_text()).group(1))")"

if command -v airbyte-cdk >/dev/null 2>&1; then
    CDK="airbyte-cdk"
elif [ -x .venv/bin/airbyte-cdk ]; then
    CDK=".venv/bin/airbyte-cdk"
else
    CDK="poetry run airbyte-cdk"
fi

$CDK image build --tag "${TAG}"
docker tag "${REPO}:${TAG}" "${REPO}:dev"
echo "built ${REPO}:${TAG} and tagged as ${REPO}:dev"
