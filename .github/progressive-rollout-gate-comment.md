<!-- progressive-rollout-gate:{{ .connector }} -->

> [!IMPORTANT]
> Active progressive rollout warning for .
>
> To bypass this warning, click on the checkbox in the PR description - or read below for more information.

**Detected `{{ .connector }}` Active Rollout: `{{ .active_rollout }}`**

- Rollout version: `{{ .rollout_docker_image_tag }}`
- Rollout state: `{{ .rollout_state }}`

**Version on `master` Branch: `{{ .master_version }}`**

- Master RC marker: `{{ .master_rc_marker }}`

**Bypass Checkbox Checked: `{{ .bypass_ack_checked }}`**

To bypass this warning, click on the checkbox in the PR description with the text:

> {{ .ack_checkbox_text }} here.

<details>
<summary>**ℹ️ More Info**</summary>

<details>
<summary>🤔 What happens if this PR is merged?</summary>

Checking the ACK box does not stop the active rollout by itself. It only allows this workflow's required check to pass. If the PR then merges, the result depends on what connector version is published after merge.

Expected outcomes by version-change type:

<details><summary>**If connector version is not modified in this PR...**</summary>

No new connector version should be released, and the active rollout should continue unchanged.

<details><summary>**If the connector version changes from RC to non-RC (GA) version...**</summary>

The merged PR may publish the GA version and make it default for eligible non-pinned actors. The existing rollout is not stopped immediately by the merge, but the rollout worker can later cancel it as superseded when finalizing.

<details><summary>**If the connector version increments to a higher `-rc` version...**</summary>

The merged PR may publish a new release candidate and replace the active RC marker. The previous incomplete rollout is canceled without unpinning, and a new rollout is created for RCn+1.

<details><summary>**🔁 How can I rerun this check?**</summary>

To rerun the check, simple check and uncheck the box, or else modify the PR description and/or title in any way.

Alternatively, you can find the Active Progressive Rollout CI workflow and manually rerun it (although this is generally slower than the above methods).

</details>

[Workflow run]({{ .workflow_run_url }})
