#!/usr/bin/env bash
#
# Evaluate the aggregate result of the connector CI checks and print
# 'result=success' or 'result=failure' to stdout and to $GITHUB_OUTPUT.
#
# Gating policy:
#
# | Job                        | Blocking | 'skipped' or 'cancelled' |
# | -------------------------- | -------- | ------------------------- |
# | generate-matrix            | yes      | failure                  |
# | jvm-connectors-test        | yes      | failure                  |
# | non-jvm-connectors-test    | yes      | failure                  |
# | connectors-lint            | yes      | failure                  |
# | connector-qa-checks        | yes      | failure                  |
# | cdk-prerelease-check       | no       | not evaluated            |
# | build-and-verify-artifacts | no       | not evaluated            |
#
# Every blocking job runs its matrix once as a no-op when no connector is
# modified, so none of them has a legitimate reason to be skipped or
# cancelled: any result other than 'success' fails the summary.

set -o pipefail

result=success

fail() {
  echo "::error::$1"
  result=failure
}

for job in \
  "generate-matrix=${GENERATE_MATRIX_RESULT:-}" \
  "jvm-connectors-test=${JVM_CONNECTORS_TEST_RESULT:-}" \
  "non-jvm-connectors-test=${NON_JVM_CONNECTORS_TEST_RESULT:-}" \
  "connectors-lint=${CONNECTORS_LINT_RESULT:-}" \
  "connector-qa-checks=${CONNECTOR_QA_CHECKS_RESULT:-}"; do
  [[ "${job#*=}" == "success" ]] && continue
  fail "Job '${job%%=*}' reported '${job#*=}', expected 'success'."
done

# A pull request that adds or modifies connector code must produce a non-empty
# connector matrix. An empty one means no connector was ever tested.
if [[ "${CONNECTOR_FILES_CHANGED:-}" == "true" && "${CONNECTORS_FOUND:-}" != "true" ]]; then
  fail "Connector files were added or modified, but the connector matrix was empty, so no connector was tested."
fi

echo "result=${result}" | tee -a "${GITHUB_OUTPUT:-/dev/null}"
