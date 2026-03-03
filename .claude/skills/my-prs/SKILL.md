---
name: my-prs
description: List PRs opened today that are assigned to me or the move-destinations team, excluding external contributors
disable-model-invocation: true
allowed-tools: Bash(gh:*), Bash(date:*), Read
argument-hint: [days-back]
---

# My PRs - Daily PR Review Dashboard

This skill fetches and displays PRs that need your attention:

1. **PRs assigned directly to you** (@frifriSF59)
2. **PRs with review requested from the move-destinations team**

All results are filtered to:
- Only show PRs opened today (or within `$ARGUMENTS` days if specified)
- Exclude PRs from users who are not members of the airbytehq organization

## Execution

Run the fetch script to get the PR list:

```bash
bash .claude/skills/my-prs/scripts/fetch-prs.sh
```

If an argument is provided (number of days), modify the date filter accordingly:
- `$ARGUMENTS` = number of days to look back (default: 0 = today only)
- Example: `/my-prs 3` looks at PRs from the last 3 days

For custom date ranges, use:
```bash
gh pr list --repo airbytehq/airbyte --assignee @me --search "created:>=YYYY-MM-DD" --json number,title,author,url
```

## After Fetching

After displaying the PRs, offer to:
1. Open a specific PR in the browser (`gh pr view <number> --web`)
2. Show details of a specific PR (`gh pr view <number>`)
3. Show the diff of a specific PR (`gh pr diff <number>`)
4. Check CI status (`gh pr checks <number>`)

## Quick Actions

The user may want to:
- **Review a PR**: Use `/review <pr-number>` if available
- **Check PR comments**: `gh pr view <number> --comments`
- **See who approved**: `gh pr view <number> --json reviews --jq '.reviews[] | select(.state=="APPROVED") | .author.login'`
