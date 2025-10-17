## ⚠️ PR Configuration Issue Detected

Hi @{{ .pr_author }}, thank you for your contribution from **{{ .repo_name }}**!

We've detected an issue with your PR configuration that will slow down the review process. Airbyte maintainers need the ability to push commits directly to your PR branch to apply formatting fixes, dependency updates, and other minor changes.

{{ if eq .is_org_fork "true" }}
### 🏢 Organization Fork Detected

Your PR is from an **organization fork** rather than a personal fork. GitHub does not allow maintainers to commit directly to branches in organization forks, even when the "Allow edits from maintainers" option is enabled.

**How to Fix:**
1. Fork the Airbyte repository under your personal GitHub account (not your organization)
2. Push your branch to your personal fork
3. Create a new PR from your personal fork

This allows us to push fixes directly to your branch, significantly speeding up the review process.
{{ end }}

{{ if eq .missing_maintainer_edit "true" }}
### 🔒 Maintainer Edits Not Allowed

Your PR does not have the "Allow edits from maintainers" option enabled. This prevents us from pushing fixes directly to your branch.

**How to Fix:**
1. On your PR page, look for the sidebar on the right
2. Find the checkbox labeled "Allow edits from maintainers"
3. Check the box to enable maintainer edits

If you don't see this option, it may be because your PR is from an organization fork (see above).
{{ end }}

### Why This Matters

Without the ability to push to your branch, we have to ask you to make changes for:
- Running `/format-fix` to fix linting issues
- Updating dependencies when conflicts arise  
- Applying small suggested changes during review

This creates unnecessary back-and-forth and slows down the time to merge your contribution.

### Need Help?

If you have questions or need assistance, please:
- Ask in the PR comments
- Join our [Slack community](https://airbytehq.slack.com/)
- Review our [Contributing Guide](https://docs.airbyte.com/platform/contributing-to-airbyte)

Thank you for your understanding and for contributing to Airbyte! 🙏
