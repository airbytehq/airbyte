<!-- block-release-check -->

## ⚠️ Release Blocked for Modified Connectors

@{{PR_AUTHOR}} — the following connector(s) modified in this PR are **blocked from release**. Publishing will be skipped for these connectors when this PR is merged.

| Connector | Reason | Yanked Version |
|-----------|--------|----------------|
{{BLOCKED_TABLE}}

<details>
<summary>What does this mean?</summary>

A `block-release.yaml` marker file exists in the connector directory, which prevents the publish pipeline from releasing the connector. This is typically because a previous version was yanked due to a bug, and the broken code still lives on master.

**To unblock:** Fix the underlying issue, then remove the `block-release.yaml` file (either manually in a PR or via the "unblock-release" workflow).

**If your PR fixes the issue:** Include the removal of `block-release.yaml` in this PR to unblock publishing.
</details>
