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
- Rollout last updated by: `{{ .rollout_updated_by }}`
- [Open Connector Rollout Manager in Retool]({{ .retool_url }}) to clean up or close out this rollout if appropriate.

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

<details><summary>If the connector version increments to a higher `-rc` version...</summary>

After this PR is merged, the new RC will be published and registered, replacing the active RC marker. When the new RC is registered, the platform cancels any existing non-terminal rollout for this connector without unpinning actors.

After merging, you still need to start the new rollout. During start, pinned actors from the previous rollout can be moved to the new RC.

</details>

<details><summary>If the connector version changes from RC to non-RC (GA) version...</summary>

You should not merge the PR unless/until the RC has been finalized as canceled. See above `Rollout state` for detected status.

> [!Warning]
> This PR should not be merged if the RC rollout is still active. First finalize the active rollout as successful or cancel it in [Connector Rollout Manager]({{ .retool_url }}).

When you finalize an RC rollout as successful, the platform triggers a promotion workflow that strips the `-rc` suffix, removes stable-version `registryOverrides`, disables progressive rollout, force-merges that promotion, and unpins actors.

</details>

#### 🔁 How to rerun this check

To rerun the check, simply check and uncheck the box, or else modify the PR description and/or title in any way.

Alternatively, you can find the Active Progressive Rollout CI workflow and manually rerun it (although this is generally slower than the above methods).

</details>

---

This comment will be updated as PR and/or rollout status changes.

[Workflow run]({{ .workflow_run_url }})
