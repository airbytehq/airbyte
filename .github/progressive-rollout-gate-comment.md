<!-- progressive-rollout-gate:{{ .connector }} -->

## Detected `{{ .connector }}` Active Rollout: `{{ .active_rollout }}`

> [!IMPORTANT]
> Active progressive rollout warning for `{{ .connector }}`.
>
> To bypass this warning, click on the matching checkbox in the PR description. Look for the checkbox text:
>
> > {{ .ack_checkbox_text }}

- Rollout version: `{{ .rollout_docker_image_tag }}`
- Rollout state: `{{ .rollout_state }}`

### Version on `master` Branch: `{{ .master_version }}`

- RC marker on `master` branch: `{{ .master_rc_marker }}`

### PR Description Checkbox Status

- Bypass checkbox checked: `{{ .bypass_ack_checked }}`

### ℹ️ More Information

<details><summary>Show/hide details...</summary>

#### 🤔 What happens if this PR is merged

Checking the checkbox will allow the PR to merge, but it does not necessarily stop the active rollout by itself. The result of the PR merging depends on what connector version is published.

Expected outcomes by type of version number change:

<details><summary>If connector version is not modified in this PR...</summary>

No new connector version should be released, and the active rollout should continue unchanged.

</details>

<details><summary>If the connector version changes to the active RC's version stem...</summary>

The active rollout is not stopped immediately by the merge.

- If this PR removes the stable-version `registryOverrides` and disables progressive rollout, the published GA version can become the default for eligible non-pinned actors.
- If this PR leaves stable-version `registryOverrides` in place or leaves progressive rollout enabled, non-rollout registry consumers should continue to see the pre-RC stable version.
- Actors already pinned by the active rollout remain pinned; publishing the GA version does not immediately unpin them.
- If the rollout later finalizes as promoted and the platform default matches this version, the rollout succeeds and unpins actors.

</details>

<details><summary>If the connector version changes from RC to a new (distinct) GA version...</summary>

The active rollout is not stopped immediately by the merge.

- If this PR removes the stable-version `registryOverrides` and disables progressive rollout, the published GA version can become the default for eligible non-pinned actors.
- If this PR leaves stable-version `registryOverrides` in place or leaves progressive rollout enabled, non-rollout registry consumers should continue to see the pre-RC stable version.
- Actors already pinned by the active rollout remain pinned; publishing a distinct GA version does not immediately unpin them.
- If the rollout later finalizes as promoted and the platform default is still this distinct GA version, the rollout is canceled as superseded.

</details>

<details><summary>If the connector version increments to a higher `-rc` version...</summary>

After this PR is merged, the new RC will be published and registered, replacing the active RC marker. When the new RC is registered, the platform cancels any existing non-terminal rollout for this connector without unpinning actors.

After merging, you still need to start the new rollout. During start, pinned actors from the previous rollout can be moved to the new RC.

</details>

#### 🔁 How to rerun this check

To rerun the check, simply check and uncheck the box, or else modify the PR description and/or title in any way.

Alternatively, you can find the Active Progressive Rollout CI workflow and manually rerun it (although this is generally slower than the above methods).

</details>

---

This comment will be updated as PR and/or rollout status changes.

[Workflow run]({{ .workflow_run_url }})
