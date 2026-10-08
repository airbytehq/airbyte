#!/usr/bin/env bash
set -euo pipefail

: "${REPO:?REPO is required}"
: "${PR_NUMBER:?PR_NUMBER is required}"
: "${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}"

[[ "$REPO" == */* && "${REPO#*/}" != */* ]] || {
  echo "::error::REPO must be in owner/name form."
  exit 1
}
[[ "$PR_NUMBER" =~ ^[1-9][0-9]*$ ]] || {
  echo "::error::PR_NUMBER must be a positive integer."
  exit 1
}

if [[ -n "${REVIEW_THREADS_FIXTURE:-}" ]]; then
  response="$(jq -ce '.' "$REVIEW_THREADS_FIXTURE")"
else
  : "${GH_TOKEN:?GH_TOKEN is required}"
  owner="${REPO%%/*}"
  name="${REPO#*/}"
  query=$(cat <<'GRAPHQL'
query($owner: String!, $name: String!, $number: Int!, $after: String = null) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          isResolved
          comments(first: 100) {
            pageInfo {
              hasNextPage
            }
            nodes {
              body
              url
              author {
                __typename
                login
              }
            }
          }
        }
      }
      reviews(last: 100) {
        nodes {
          body
          author {
            __typename
          }
        }
      }
      comments(last: 100) {
        nodes {
          body
          author {
            __typename
          }
        }
      }
    }
  }
}
GRAPHQL
)
  all_threads='[]'
  cursor=''

  while true; do
    api_args=(-f "query=$query" -F "owner=$owner" -F "name=$name" -F "number=$PR_NUMBER")
    [[ -z "$cursor" ]] || api_args+=(-F "after=$cursor")
    response="$(gh api graphql "${api_args[@]}")"
    page_threads="$(jq -ce '.data.repository.pullRequest.reviewThreads.nodes' <<<"$response")"
    all_threads="$(jq -cn --argjson all "$all_threads" --argjson page "$page_threads" '$all + $page')"
    has_next="$(jq -er '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage' <<<"$response")"
    [[ "$has_next" == true ]] || break
    cursor="$(jq -er '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor | select(type == "string" and length > 0)' <<<"$response")"
  done

  review_summaries="$(jq -c '.data.repository.pullRequest.reviews.nodes // []' <<<"$response")"
  issue_comments="$(jq -c '.data.repository.pullRequest.comments.nodes // []' <<<"$response")"
  response="$(jq -cn \
    --argjson nodes "$all_threads" \
    --argjson reviews "$review_summaries" \
    --argjson comments "$issue_comments" \
    '{data:{repository:{pullRequest:{reviewThreads:{nodes:$nodes},reviews:{nodes:$reviews},comments:{nodes:$comments}}}}}')"
fi

threads="$(jq -ce '.data.repository.pullRequest.reviewThreads.nodes' <<<"$response")"
jq -e 'all(.[]; (.comments.pageInfo.hasNextPage // false) == false)' <<<"$threads" >/dev/null || {
  echo "::error::A review thread has more than 100 comments; refusing to evaluate an incomplete conversation."
  exit 1
}

marker_threads="$(jq -ce '
  def parse_marker:
    try capture("<!-- breaking-change-review:recommendation id=\"(?<id>R[1-9][0-9]*)\" title=\"(?<title>[^\"\\r\\n]+)\" -->")
    catch null;
  [
    .[] as $thread
    | ($thread.comments.nodes // []) as $comments
    | ($comments[0].body // "") as $first_body
    | if ($first_body | contains("<!-- breaking-change-review:recommendation")) then
        ($first_body | parse_marker) as $marker
        | if $marker == null then
            error("A recommendation marker is present but does not match the required format.")
          else
            [$comments[1:][] | select(.author.__typename == "User")] as $human_replies
            | {
                id: $marker.id,
                title: $marker.title,
                url: ($comments[0].url // ""),
                isResolved: $thread.isResolved,
                hasHumanReply: ($human_replies | length > 0),
                latestHumanReply: ($human_replies[-1].body // "")
              }
          end
      else empty
      end
  ]
' <<<"$threads")"

jq -e 'map(.id) | length == (unique | length)' <<<"$marker_threads" >/dev/null || {
  echo "::error::Recommendation thread IDs are not unique."
  exit 1
}

conversation_count="$(jq -er 'length' <<<"$marker_threads")"
failing_threads="$(jq -ce '
  [
    .[]
    | select((.isResolved != true) or (.hasHumanReply != true))
    | . + {
        status: (
          if .hasHumanReply and (.isResolved != true) then "replied, not resolved"
          elif (.hasHumanReply != true) and .isResolved then "resolved without a reply"
          else "no reply yet"
          end
        )
      }
  ]
' <<<"$marker_threads")"
failing_count="$(jq -er 'length' <<<"$failing_threads")"

write_output() {
  printf '%s=%s\n' "$1" "$2" | tee -a "$GITHUB_OUTPUT"
}

write_multiline_output() {
  local key="$1"
  local value="$2"
  local delimiter
  delimiter="EOF_$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')"
  while [[ "$value" == *"$delimiter"* ]]; do
    delimiter="EOF_$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')"
  done
  {
    printf '%s<<%s\n' "$key" "$delimiter"
    printf '%s\n' "$value"
    printf '%s\n' "$delimiter"
  } >>"$GITHUB_OUTPUT"
}

if [[ "$conversation_count" == 0 ]]; then
  if jq -e '
    [
      (.data.repository.pullRequest.reviews.nodes // [])[],
      (.data.repository.pullRequest.comments.nodes // [])[]
    ]
    | any(.[]; .author.__typename == "Bot" and ((.body // "") | contains("<!-- breaking-change-review:summary -->")))
  ' <<<"$response" >/dev/null; then
    result="ready"
    status_body="**Ready for human review.** The breaking-change review had nothing for the author to resolve. The breaking-change reviewers have been pinged in Slack.

<sub>A resolved conversation means the author answered it, not that a reviewer agreed. Sign-off stays with @airbytehq/breaking-change-reviewers.</sub>"
    printf 'Gate result: the review had nothing for the author to resolve.\n%s\n' "$status_body"
  else
    result="none"
    status_body="> No breaking-change review conversations found on this PR. Run /ai-breaking-change-review first."
    echo "$status_body"
  fi
elif [[ "$failing_count" != 0 ]]; then
  result="blocked"
  bullets="$(jq -r '.[] | "- **\(.id)** ([\(.title)](\(.url))): \(.status)"' <<<"$failing_threads")"
  status_body="**Not ready for review yet.** $failing_count of $conversation_count conversations are still open:

$bullets

Reply in each one, resolve it, then run /ai-breaking-change-ready again."
  printf 'Gate result: %s of %s recommendation conversations are not ready.\n%s\n' \
    "$failing_count" "$conversation_count" "$status_body"
else
  result="ready"
  status_body="**Ready for human review.** All $conversation_count conversations have a reply and are resolved.

<sub>A resolved conversation means the author answered it, not that a reviewer agreed. Sign-off stays with @airbytehq/breaking-change-reviewers.</sub>"
  printf 'Gate result: all %s recommendation conversations have a human reply and are resolved.\n%s\n' \
    "$conversation_count" "$status_body"
fi

write_output "result" "$result"
write_output "conversation_count" "$conversation_count"
write_output "failing_count" "$failing_count"
write_output "replies_b64" "$(jq -c '[.[] | select(.isResolved == true and .hasHumanReply == true)]' <<<"$marker_threads" | base64 -w0)"
write_multiline_output "status_body" "$status_body"
