#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../../.." && pwd)"
gate_script="$repo_root/.github/scripts/check-breaking-change-ready.sh"
stub_dir="$script_dir/bin"
cases_dir="$script_dir/cases"
failures=0

for case_dir in "$cases_dir"/*/; do
  case_name="${case_dir%/}"
  case_name="${case_name##*/}"
  output_file="$(mktemp)"
  temp_dir="$(mktemp -d)"
  calls_log="$temp_dir/calls.log"
  : >"$calls_log"

  if output="$(
    PATH="$stub_dir:$PATH" \
      GH_TOKEN=dummy \
      REPO=airbytehq/airbyte \
      PR_NUMBER=1 \
      GITHUB_OUTPUT="$output_file" \
      GH_STUB_FIXTURE_DIR="${case_dir%/}" \
      GH_STUB_CALLS_LOG="$calls_log" \
      bash "$gate_script" 2>&1
  )"; then
    exit_code=0
  else
    exit_code=$?
  fi

  expected_exit_code=0
  case_passed=true
  while IFS='=' read -r key value || [[ -n "$key" ]]; do
    case "$key" in
      result|conversation_count|failing_count)
        actual="$(awk -F= -v key="$key" '$1 == key { sub(/^[^=]*=/, ""); print; exit }' "$output_file")"
        if [[ "$actual" != "$value" ]]; then
          printf 'FAIL %s: expected %s=%s, got %s\n' "$case_name" "$key" "$value" "${actual:-<missing>}"
          case_passed=false
        fi
        ;;
      exit_code)
        if [[ "$value" == nonzero ]]; then
          if [[ "$exit_code" == 0 ]]; then
            printf 'FAIL %s: expected a nonzero exit code\n' "$case_name"
            case_passed=false
          fi
        else
          expected_exit_code="$value"
        fi
        ;;
      pages_fetched)
        actual="$(wc -l <"$calls_log" | tr -d ' ')"
        if [[ "$actual" != "$value" ]]; then
          printf 'FAIL %s: expected %s pages fetched, got %s\n' "$case_name" "$value" "$actual"
          case_passed=false
        fi
        ;;
      output_contains)
        if [[ "$output" != *"$value"* ]]; then
          printf 'FAIL %s: output did not contain %s\n' "$case_name" "$value"
          case_passed=false
        fi
        ;;
      *)
        printf 'FAIL %s: unsupported expectation key %s\n' "$case_name" "$key"
        case_passed=false
        ;;
    esac
  done <"$case_dir/expected"

  if [[ "$expected_exit_code" != 0 && "$exit_code" != "$expected_exit_code" ]]; then
    printf 'FAIL %s: expected exit code %s, got %s\n' "$case_name" "$expected_exit_code" "$exit_code"
    case_passed=false
  fi

  if [[ "$case_passed" == true ]]; then
    printf 'PASS %s\n' "$case_name"
  else
    printf '%s\n' '--- script output ---' "$output" '--- GITHUB_OUTPUT ---'
    cat "$output_file"
    failures=$((failures + 1))
  fi

  rm -f "$output_file"
  rm -rf "$temp_dir"
done

if [[ "$failures" != 0 ]]; then
  printf '%s test case(s) failed.\n' "$failures"
  exit 1
fi
