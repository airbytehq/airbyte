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

### ⚠️ What happens if you merge this PR now

If this PR publishes a **new `-rc` version** of `{{ .connector }}`:

1. The new RC is published and registered as the release candidate.
2. **The rollout of `{{ .rollout_docker_image_tag }}` is auto-cancelled**, not finalized. Registering the new RC cancels every non-terminal rollout for this connector with `errorMsg = "Rollout was incomplete when a new rollout was started. Cancelled without unpinning."`
3. **Actors already pinned to `{{ .rollout_docker_image_tag }}` stay pinned to it.** Cancellation does not unpin, so those connections keep syncing on the old RC image — they are *not* rolled back to the previous GA version, and they are *not* moved to the new RC by the merge itself.
4. Nothing rolls out on its own. A new rollout is created in `initialized` and must be started (autopilot or manually in [Connector Rollout Manager]({{ .retool_url }})). Starting it migrates the previous rollout's pins onto the new RC by default (`migratePins`), which is what moves those stranded actors forward. Until then, they stay on the old RC.

If this PR removes the `-rc` suffix (RC → GA), or does not change the version at all, see the other cases in **More Information** below.

To avoid stranded pins, finalize or cancel the active rollout in [Connector Rollout Manager]({{ .retool_url }}) before merging.

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

See the "What happens if you merge this PR now" section above: the new RC replaces the active RC marker, the in-flight rollout is cancelled without unpinning, and the new rollout still has to be started before the previously pinned actors move onto the new RC.

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
