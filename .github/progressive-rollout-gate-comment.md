<!-- progressive-rollout-gate:{{ .connector }} -->

> [!IMPORTANT]
> Active progressive rollout warning for `{{ .connector }}`.
>
> To bypass this warning, check the matching box in the PR description.

**Rollout status**

- Active rollout: `{{ .active_rollout }}`
- Rollout version: `{{ .rollout_docker_image_tag }}`
- Rollout state: `{{ .rollout_state }}`
- Version on `master`: `{{ .master_version }}`
- Master RC marker: `{{ .master_rc_marker }}`
- Bypass checkbox checked: `{{ .bypass_ack_checked }}`

Checkbox text:

> {{ .ack_checkbox_text }}

<details>
<summary>What happens if this PR merges?</summary>

Checking the ACK box does not stop the active rollout by itself. It only allows this workflow's required check to pass. If the PR merges, the result depends on what connector version is published after merge.

Expected outcomes by version-change type:

- If this PR does not change the connector version, no new connector version should be released and the active rollout should continue unchanged.
- If this PR promotes an RC to a GA version, the merged PR may publish the GA version and make it default for eligible non-pinned actors. The existing rollout is not stopped immediately by the merge, but the rollout worker can later cancel it as superseded when finalizing.
- If this PR increments to a higher `-rc` version, the merged PR may publish a new release candidate and replace the active RC marker. The previous incomplete rollout is canceled without unpinning, and a new rollout is created for the next RC.

</details>

<details>
<summary>How can I rerun this check?</summary>

To rerun the check, check and uncheck the box, or edit the PR description or title.

You can also rerun the Active Progressive Rollout CI workflow manually, although that is usually slower.

</details>

[Workflow run]({{ .workflow_run_url }})
