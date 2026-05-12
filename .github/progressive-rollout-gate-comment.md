<!-- progressive-rollout-gate:{{ .connector }} -->

## Detected `{{ .connector }}` Active Rollout: `{{ .active_rollout }}`**

> [!IMPORTANT]
> Active progressive rollout warning for `{{ .connector }}`.
>
> To bypass this warning, check the matching box in the PR description.

<<<<<<< HEAD
- Rollout version: `{{ .rollout_docker_image_tag }}`
- Rollout state: `{{ .rollout_state }}`

### Version on `master` Branch: `{{ .master_version }}`

=======
**Rollout status**

- Active rollout: `{{ .active_rollout }}`
- Rollout version: `{{ .rollout_docker_image_tag }}`
- Rollout state: `{{ .rollout_state }}`
- Version on `master`: `{{ .master_version }}`
>>>>>>> b0dee443a3c089009d375799aeee7eeb09c49758
- Master RC marker: `{{ .master_rc_marker }}`
- Bypass checkbox checked: `{{ .bypass_ack_checked }}`

<<<<<<< HEAD
### Bypass Checkbox Checked: `{{ .bypass_ack_checked }}`
=======
Checkbox text:
>>>>>>> b0dee443a3c089009d375799aeee7eeb09c49758

> {{ .ack_checkbox_text }}

<<<<<<< HEAD
### ℹ️ More Info

<details>
<summary>Show/hide additional information...</summary>

#### 🤔 What happens if this PR is merged
=======
<details>
<summary>What happens if this PR merges?</summary>

Checking the ACK box does not stop the active rollout by itself. It only allows this workflow's required check to pass. If the PR merges, the result depends on what connector version is published after merge.
>>>>>>> b0dee443a3c089009d375799aeee7eeb09c49758

Checking the checkbox will allow the PR to merge, but it does not necessarily stop the active rollout by itself.

<<<<<<< HEAD
The result of the PR merging depends on what connector version is published.

Expected outcomes by type of version number change:

<details><summary>If connector version is not modified in this PR...</summary>

No new connector version should be released, and the active rollout should continue unchanged.
</details>

<details><summary>If the connector version changes from RC to non-RC (GA) version...</summary>

The merged PR may publish the GA version and make it default for eligible non-pinned actors. The existing rollout is not stopped immediately by the merge, but the rollout worker can later cancel it as superseded when finalizing.
</details>

<details><summary>If the connector version increments to a higher `-rc` version...</summary>

The merged PR may publish a new release candidate and replace the active RC marker. The previous incomplete rollout is canceled without unpinning, and a new rollout is created for RCn+1.
</details>

### 🔁 How to rerun this check

To rerun the check, simply check and uncheck the box, or else modify the PR description and/or title in any way.

Alternatively, you can find the Active Progressive Rollout CI workflow and manually rerun it (although this is generally slower than the above methods).
=======
- If this PR does not change the connector version, no new connector version should be released and the active rollout should continue unchanged.
- If this PR promotes an RC to a GA version, the merged PR may publish the GA version and make it default for eligible non-pinned actors. The existing rollout is not stopped immediately by the merge, but the rollout worker can later cancel it as superseded when finalizing.
- If this PR increments to a higher `-rc` version, the merged PR may publish a new release candidate and replace the active RC marker. The previous incomplete rollout is canceled without unpinning, and a new rollout is created for the next RC.

</details>

<details>
<summary>How can I rerun this check?</summary>

To rerun the check, check and uncheck the box, or edit the PR description or title.

You can also rerun the Active Progressive Rollout CI workflow manually, although that is usually slower.
>>>>>>> b0dee443a3c089009d375799aeee7eeb09c49758

</details>

-----

This comment will be updated as PR and/or rollout status changes.

[Workflow run]({{ .workflow_run_url }})
