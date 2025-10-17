## ⚠️ PR Configuration Issue Detected

Hi @{{ .pr_author }}, thank you for your contribution from **{{ .repo_name }}**!

We've detected an issue with your PR configuration that is a barrier to effective and efficient review. To streamline your PR review and acceptance, Airbyte maintainers require the ability to push commits directly to your PR branch to apply formatting fixes, dependency updates, security patches, and other minor changes.

Specific details of the issue detected in your PR:

{{ if eq .is_org_fork "true" }}
### 🏢 Organization Fork Detected

We have detected that your PR is from an **organization fork** rather than a personal fork. GitHub does not allow maintainers to commit directly to branches in organization forks. [Learn more about allowing changes to a pull request branch created from a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork).

**How to Fix:**
1. Fork the Airbyte repository under your personal GitHub account (not your organization).
2. Push your branch to your personal fork.
3. Create a new PR from your personal fork.

This will allow Airbyte maintainers to push any necessary fixes directly to your branch, significantly speeding up the review process.
{{ end }}

{{ if eq .missing_maintainer_edit "true" }}
### 🔒 Maintainer Edits Not Allowed

We have detected that your PR does not have the "Allow edits from maintainers" option enabled. This prevents us from pushing fixes directly to your branch.

**How to Fix:**
1. On your PR page, look for the sidebar on the right.
2. Find the checkbox labeled "Allow edits from maintainers".
3. Check the box to enable maintainer edits.
4. Close and reopen your PR to rerun this check. (No need to recreate the PR.)

After completing these steps, you should see a green checkmark (✅) on the "**PR Permissions Check**" PR check below. This signifies that maintainers will be able to push necessary fixes directly to your branch, enabling a more efficient review process.

{{ end }}

### Need Help?

If you have questions or need assistance, please:
- Ask in the PR comments.
- Join our [Slack community](https://airbytehq.slack.com/).
- Review our [Contributing Guide](https://docs.airbyte.com/platform/contributing-to-airbyte).

Thank you for your understanding and for contributing to Airbyte! 🙏
