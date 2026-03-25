#!/usr/bin/env bash
# Debug a failed Airbyte destination check connection job (e.g. in Kubernetes).
#
# Usage:
#   ./scripts/debug_check_connection.sh [pod-name-prefix]
#
# Example (your pod):
#   ./scripts/debug_check_connection.sh azure-onelake-spec-b40a3ecb-22b5-442d-b0b1-ebb8d6e92b78-0
#
# Or with kubectl already configured:
#   kubectl logs -l job-name=<job-name> --all-containers=true --tail=200
#   kubectl describe pod <pod-name>

set -e
PREFIX="${1:-azure-onelake}"
CONTEXT="${KUBE_CONTEXT:-}"

echo "=== Looking for pods matching prefix: $PREFIX ==="
if [[ -n "$CONTEXT" ]]; then
  kubectl --context "$CONTEXT" get pods -A | grep -i "$PREFIX" || true
  NS=$(kubectl --context "$CONTEXT" get pods -A -o name | grep -i "$PREFIX" | head -1 | cut -d/ -f1 | cut -d' ' -f1)
  POD=$(kubectl --context "$CONTEXT" get pods -A -o name | grep -i "$PREFIX" | head -1 | cut -d/ -f2)
else
  kubectl get pods -A | grep -i "$PREFIX" || true
  POD=$(kubectl get pods -A -o name | grep -i "$PREFIX" | head -1)
fi

if [[ -z "$POD" ]]; then
  echo "No pod found. Try: kubectl get pods -A | grep onelake"
  exit 1
fi

# If POD is "namespace/name"
if [[ "$POD" == *"/"* ]]; then
  NS="${POD%%/*}"
  POD="${POD##*/}"
else
  NS="${NAMESPACE:-default}"
fi

echo ""
echo "=== Pod: $NS/$POD ==="
if [[ -n "$CONTEXT" ]]; then
  kubectl --context "$CONTEXT" -n "$NS" describe pod "$POD" | tail -50
else
  kubectl -n "$NS" describe pod "$POD" | tail -50
fi

echo ""
echo "=== Logs (all containers, last 150 lines) ==="
if [[ -n "$CONTEXT" ]]; then
  kubectl --context "$CONTEXT" -n "$NS" logs "$POD" --all-containers=true --tail=150 2>/dev/null || \
  kubectl --context "$CONTEXT" -n "$NS" logs "$POD" --tail=150 2>/dev/null
else
  kubectl -n "$NS" logs "$POD" --all-containers=true --tail=150 2>/dev/null || \
  kubectl -n "$NS" logs "$POD" --tail=150 2>/dev/null
fi
