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

Checking the checkbox will allow the PR to merge, but it does not stop the active rollout by itself. The rollout worker is not notified just because another PR publishes a GA version; it only notices a superseding default version later if this rollout itself finalizes as promoted.

Expected outcomes by type of version number change:

<details><summary>If connector version is not modified in this PR...</summary>

No new connector version should be released, and the active rollout should continue unchanged.

</details>

<details><summary>If the connector version changes from RC to non-RC (GA) version...</summary>

The merged PR may publish a GA version, but the active rollout is not stopped immediately by the merge.

During an active RC rollout, `registryOverrides.cloud.dockerImageTag` and `registryOverrides.oss.dockerImageTag` usually pin non-rollout registry consumers to the pre-RC stable version. Older registry generation depended on those overrides to prevent the RC from becoming default. The newer `airbyte-ops registry compile` path is semver-aware, so `-rc` versions are not eligible as GA/default/latest versions. It also skips GA versions whose metadata still has progressive rollout enabled. If this PR removes those overrides and disables progressive rollout, the newly published GA version can become the registry default for eligible non-pinned actors.

If the active rollout later finalizes as promoted, the rollout worker polls the platform default version and compares it to this rollout's RC stem. For example, `1.2.3-rc.1` is expected to become `1.2.3`. If the default is a different GA version, the rollout is marked `CANCELED` as superseded. If the default matches the RC stem, the rollout can complete as promoted.

</details>

<details><summary>If the connector version increments to a higher `-rc` version...</summary>

The merged PR may publish a new release candidate and replace the active RC marker. The active rollout is not stopped just because the RC marker changes; it must still be explicitly finalized, canceled, or superseded during its own promote finalization path. Actors already pinned by the active rollout remain pinned until that rollout finalizes or is canceled.

</details>

#### 🔁 How to rerun this check

To rerun the check, simply check and uncheck the box, or else modify the PR description and/or title in any way.

Alternatively, you can find the Active Progressive Rollout CI workflow and manually rerun it (although this is generally slower than the above methods).

</details>

---

This comment will be updated as PR and/or rollout status changes.

[Workflow run]({{ .workflow_run_url }})
