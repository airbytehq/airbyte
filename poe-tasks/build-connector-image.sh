#!/usr/bin/env bash
set -Eeuo pipefail

RED="❌"; GREEN="✅"; INFO="ℹ️"; HAMMER="🛠️"; WHALE="🐳"; SPARKLES="✨"

die() { echo "${RED} $*"; exit 1; }
log() { echo "${INFO} $*"; }

command -v docker >/dev/null 2>&1 || die "Docker is not installed or not on PATH."
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "${REPO_ROOT}" ]] || die "Not inside the airbyte repository."
CONNECTOR_DIR="${POE_PWD:-$PWD}"
[[ -f "${CONNECTOR_DIR}/metadata.yaml" ]] || die "metadata.yaml not found in ${CONNECTOR_DIR}. Run inside a connector directory or via 'poe connector <name> image build'."

TAG=""
if [[ $# -gt 0 && "${1-}" != "--tag" ]]; then
  TAG="$1"
  shift
fi
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="$2"; shift 2;;
    *) die "Unknown argument: $1 (supported: [<tag>] or --tag <tag>)";;
  esac
done

ARCH_RAW="$(docker info --format '{{.Architecture}}' 2>/dev/null || true)"
if [[ -z "${ARCH_RAW}" ]]; then
  U="$(uname -m)"
  case "${U}" in
    x86_64|amd64) ARCH_RAW="amd64";;
    aarch64|arm64) ARCH_RAW="arm64";;
    *) die "Unsupported architecture '${U}'. Supported: amd64, arm64.";;
  esac
fi
case "${ARCH_RAW}" in
  amd64|x86_64) PLATFORM="amd64";;
  arm64|aarch64) PLATFORM="arm64";;
  *) die "Unsupported docker architecture '${ARCH_RAW}'. Supported: amd64, arm64.";;
esac
DEFAULT_TAG="dev-${PLATFORM}"
TAG="${TAG:-${DEFAULT_TAG}}"

pushd "${CONNECTOR_DIR}" >/dev/null
  command -v poe >/dev/null 2>&1 || die "poe (poethepoet) is required."
  LANGUAGE="$(poe -qq get-language)"
  BASE_IMAGE="$(poe -qq get-base-image)"
popd >/dev/null

[[ -n "${LANGUAGE}" ]] || die "Could not determine connector language."
[[ -n "${BASE_IMAGE}" ]] || die "Could not determine base image from metadata.yaml."

case "${LANGUAGE}" in
  python) DOCKERFILE_SUFFIX="python-connector";;
  java) DOCKERFILE_SUFFIX="java-connector";;
  manifest-only) DOCKERFILE_SUFFIX="manifest-only-connector";;
  *) die "Unsupported connector language: ${LANGUAGE}";;
esac

DOCKERFILE="${REPO_ROOT}/docker-images/Dockerfile.${DOCKERFILE_SUFFIX}"
[[ -f "${DOCKERFILE}" ]] || die "Dockerfile not found: ${DOCKERFILE}"

command -v yq >/dev/null 2>&1 || die "yq is required to parse metadata.yaml."
DOCKER_REPO="$(yq eval '.data.dockerRepository' "${CONNECTOR_DIR}/metadata.yaml")"
[[ -n "${DOCKER_REPO}" ]] || die "Failed to read .data.dockerRepository from metadata.yaml."
CONNECTOR_NAME="$(basename "${DOCKER_REPO}")"
FINAL_IMAGE="${DOCKER_REPO}:${TAG}"
BUILD_ARGS=( --build-arg "BASE_IMAGE=${BASE_IMAGE}" --build-arg "CONNECTOR_NAME=${CONNECTOR_NAME}" )

if [[ "${LANGUAGE}" == "java" ]]; then
  log "${HAMMER} Building Java connector tarball via Gradle..."
  ( cd "${REPO_ROOT}" && ./gradlew ":airbyte-integrations:connectors:${CONNECTOR_NAME}:distTar" )
fi

log "${WHALE} Building image for ${CONNECTOR_NAME} -> ${FINAL_IMAGE} (platform linux/${PLATFORM})"
docker buildx build \
  --platform "linux/${PLATFORM}" \
  --file "${DOCKERFILE}" \
  "${BUILD_ARGS[@]}" \
  -t "${FINAL_IMAGE}" \
  --load \
  "${CONNECTOR_DIR}"

echo "${GREEN} Build complete."
echo "${SPARKLES} Image loaded into local Docker: ${FINAL_IMAGE}"
echo "${FINAL_IMAGE}"
