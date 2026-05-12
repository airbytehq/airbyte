<!-- progressive-rollout-gate:{{ .connector }} -->

> [!IMPORTANT]
> Active progressive rollout warning for `{{ .connector }}`.
>
> This PR can bypass the warning only after the PR-description ACK checkbox is checked.

Detected signals:

- Active rollout: `{{ .active_rollout }}`
- Rollout version: `{{ .rollout_docker_image_tag }}`
- Rollout state: `{{ .rollout_state }}`
- Master version: `{{ .master_version }}`
- Master RC marker: `{{ .master_rc_marker }}`
- Bypass ACK checked: `{{ .bypass_ack_checked }}`

To bypass this warning, check this box in the PR description:

`- [ ] {{ .ack_checkbox_text }} [here]({{ .rollout_comment_url }}).`

<details>
<summary>What happens if this PR is merged?</summary>

Checking the ACK box does not stop the active rollout by itself. It only allows this workflow's required check to pass. If the PR then merges, the result depends on what connector version is published after merge.

<details>
<summary>Expected outcomes by version-change type</summary>

- No connector version change: no new connector version should be released, and the active rollout should continue unchanged.
- RC to GA: the merged PR may publish the GA version and make it default for eligible non-pinned actors. The existing rollout is not stopped immediately by the merge, but the rollout worker can later cancel it as superseded when finalizing.
- RCn to RCn+1: the merged PR may publish a new release candidate and replace the active RC marker. The previous incomplete rollout is canceled without unpinning, and a new rollout is created for RCn+1.

</details>
</details>

[Workflow run]({{ .workflow_run_url }})
