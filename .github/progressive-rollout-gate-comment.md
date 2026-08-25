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

Checking the bypass box lets this PR merge; it does not stop the active rollout by itself. What happens next depends on which version this PR publishes.

**If the connector version is not modified** — nothing new is published and the rollout of `{{ .rollout_docker_image_tag }}` continues unchanged.

**If the connector version increments to a higher `-rc` version:**

1. The new RC is published and registered as the release candidate.
2. **The rollout of `{{ .rollout_docker_image_tag }}` is auto-cancelled**, not finalized. Registering the new RC cancels every non-terminal rollout for this connector with `errorMsg = "Rollout was incomplete when a new rollout was started. Cancelled without unpinning."`
3. **Actors already pinned to `{{ .rollout_docker_image_tag }}` stay pinned to it.** Cancellation does not unpin, so those connections keep syncing on the old RC image — they are *not* rolled back to the previous GA version, and they are *not* moved to the new RC by the merge itself.
4. Nothing rolls out on its own. A new rollout is created in `initialized` and must be started (autopilot or manually in [Connector Rollout Manager]({{ .retool_url }})). Starting it migrates the previous rollout's pins onto the new RC by default (`migratePins`), which is what moves those stranded actors forward. Until then, they stay on the old RC.

To avoid stranded pins, finalize or cancel the active rollout in [Connector Rollout Manager]({{ .retool_url }}) before merging.

**If the connector version changes from `-rc` to a non-RC (GA) version** — do not merge while the rollout is still active.

> [!Warning]
> First finalize the active rollout as successful, or cancel it, in [Connector Rollout Manager]({{ .retool_url }}). See `Rollout state` above for the detected status.

Finalizing an RC rollout as successful triggers a promotion workflow that strips the `-rc` suffix, removes stable-version `registryOverrides`, disables progressive rollout, force-merges that promotion, and unpins actors — so the GA bump normally lands that way rather than through this PR.

### Version on `master` Branch: `{{ .master_version }}`

- RC marker on `master` branch: `{{ .master_rc_marker }}`

### PR Description Checkbox Status

- Bypass checkbox checked: `{{ .bypass_ack_checked }}`

### ℹ️ More Information

<details><summary>Show/hide details...</summary>

#### 🔁 How to rerun this check

To rerun the check, simply check and uncheck the box, or else modify the PR description and/or title in any way.

Alternatively, you can find the Active Progressive Rollout CI workflow and manually rerun it (although this is generally slower than the above methods).

</details>

---

This comment will be updated as PR and/or rollout status changes.

[Workflow run]({{ .workflow_run_url }})
