#!/bin/bash
# Fetch PRs opened today (or N days back) that are assigned to user or move-destinations team
# Excludes PRs from non-airbytehq org members

set -e

# Days to look back (default: 0 = today only)
DAYS_BACK=${1:-0}

# Calculate the start date
if [[ "$OSTYPE" == "darwin"* ]]; then
    START_DATE=$(date -v-${DAYS_BACK}d +%Y-%m-%d)
else
    START_DATE=$(date -d "-${DAYS_BACK} days" +%Y-%m-%d)
fi

echo "=== PRs Since ${START_DATE} ==="
echo ""

# Get org members (cached for performance)
echo "Fetching airbytehq org members..."
ORG_MEMBERS=$(gh api orgs/airbytehq/members --paginate --jq '.[].login' 2>/dev/null | sort -u)

if [ -z "$ORG_MEMBERS" ]; then
    echo "Error: Could not fetch org members. Check your GitHub authentication." >&2
    exit 1
fi

# Convert to regex pattern for matching (include known bots)
# Note: gh CLI returns bot authors as "app/bot-name" format
KNOWN_BOTS="app/devin-ai-integration|app/dependabot|app/github-actions|devin-ai-integration\[bot\]|dependabot\[bot\]|github-actions\[bot\]"
ORG_MEMBERS_PATTERN=$(echo "$ORG_MEMBERS" | tr '\n' '|' | sed 's/|$//')
ORG_MEMBERS_PATTERN="${ORG_MEMBERS_PATTERN}|${KNOWN_BOTS}"

echo "Found $(echo "$ORG_MEMBERS" | wc -l | tr -d ' ') org members (+ known bots)."
echo ""

# Function to filter and display PRs
filter_and_display_prs() {
    local prs_json="$1"

    if [ -z "$prs_json" ] || [ "$prs_json" = "[]" ]; then
        echo "(none)"
        return
    fi

    # Get count of PRs from org members
    local count=$(echo "$prs_json" | jq -c '.[]' 2>/dev/null | while read -r pr; do
        author=$(echo "$pr" | jq -r '.author.login')
        if echo "$author" | grep -qE "^($ORG_MEMBERS_PATTERN)$"; then
            echo "1"
        fi
    done | wc -l | tr -d ' ')

    if [ "$count" -eq 0 ]; then
        echo "(none from org members)"
        return
    fi

    # Display PRs from org members
    echo "$prs_json" | jq -c '.[]' 2>/dev/null | while read -r pr; do
        author=$(echo "$pr" | jq -r '.author.login')

        # Check if author is org member
        if echo "$author" | grep -qE "^($ORG_MEMBERS_PATTERN)$"; then
            number=$(echo "$pr" | jq -r '.number')
            title=$(echo "$pr" | jq -r '.title')
            url=$(echo "$pr" | jq -r '.url')
            created=$(echo "$pr" | jq -r '.createdAt' | cut -d'T' -f1)

            echo "- **#${number}**: ${title}"
            echo "  - Author: @${author} | Created: ${created}"
            echo "  - ${url}"
            echo ""
        fi
    done
}

echo "## PRs Assigned to you:"
echo ""

ASSIGNED_PRS=$(gh pr list \
    --repo airbytehq/airbyte \
    --assignee @me \
    --search "created:>=${START_DATE}" \
    --json number,title,author,url,createdAt \
    --limit 100 2>/dev/null || echo "[]")

filter_and_display_prs "$ASSIGNED_PRS"

echo ""
echo "## PRs with review requested from move-destinations team:"
echo ""

# Get move-destinations team members for individual reviewer search
TEAM_MEMBERS=$(gh api orgs/airbytehq/teams/move-destinations/members --jq '.[].login' 2>/dev/null)

# Build search query for team OR any team member as reviewer
REVIEWER_SEARCH="team-review-requested:airbytehq/move-destinations"
while IFS= read -r member; do
    [ -n "$member" ] && REVIEWER_SEARCH="${REVIEWER_SEARCH} OR review-requested:${member}"
done <<< "$TEAM_MEMBERS"

TEAM_PRS=$(gh pr list \
    --repo airbytehq/airbyte \
    --search "created:>=${START_DATE} (${REVIEWER_SEARCH})" \
    --json number,title,author,url,createdAt \
    --limit 100 2>/dev/null || echo "[]")

filter_and_display_prs "$TEAM_PRS"

echo ""
echo "---"
echo "PRs from non-airbytehq members have been excluded."
echo "Tip: Run '/my-prs 7' to see the last week's PRs."
