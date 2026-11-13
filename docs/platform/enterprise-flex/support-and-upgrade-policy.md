---
products: enterprise-flex
sidebar_label: Support and upgrade policy
---

# Enterprise Flex support and upgrade policy

In Enterprise Flex, Airbyte manages and upgrades the control plane and any Airbyte-managed data planes for you. You manage the self-managed data planes that run in your own infrastructure, including when you upgrade them. This policy explains how Airbyte publishes new data plane versions and how long Airbyte supports each one, so you can plan your upgrades.

This policy applies only to self-managed data planes you deploy with the `airbyte-data-plane` Helm chart.

## Release cadence

Airbyte aims to publish a new minor version of the data plane, like 2.4 or 2.5, approximately every two months, or about six times per year. Between minor versions, Airbyte may publish patch versions, like 2.4.1, for security issues and urgent bug fixes.

Each version has [release notes](/release_notes/) that describe what's new and anything you need to know before you upgrade.

## Support window

Airbyte supports each minor version for 14 months after it's released. The end-of-support date is known the day a version is released, and it doesn't change when Airbyte publishes patch versions for that minor version.

Fourteen months is one year plus one release interval. If you upgrade to the latest version, you have at least a year before you need to upgrade again, no matter where you are in the release cycle. Because Airbyte releases a new minor version about every two months, about seven minor versions are supported at any time.

If your data plane runs a version that's past its end-of-support date, Airbyte Support may ask you to upgrade to a supported version before it can help you troubleshoot an issue.

## Compatibility and breaking changes

Airbyte only ships changes that break data plane compatibility in a major version, like 3.0. Minor and patch versions don't break compatibility, so if you're on any supported version, you can upgrade to the latest minor version of the same major version without planning for breaking changes.

Airbyte documents breaking changes in the release notes for the major version that introduces them and in the [breaking change list](/release_notes/self-managed/breaking-changes). Review both before you upgrade to a new major version.

## Security patches

Airbyte publishes security patches only for the latest minor version of each supported major version. For example, if Airbyte supports 3.1, 2.8, and 2.7, Airbyte publishes security patches for 3.1 and 2.8. To get a security patch on 2.7, upgrade to the latest patch of 2.8.

## Supported versions

| Version | Release date       | End of support     |
| ------- | ------------------ | ------------------ |
| 2.5     | November 6, 2026   | January 6, 2028    |
| 2.4     | October 9, 2026    | December 9, 2027   |
| 2.3     | September 15, 2026 | November 15, 2027  |
| 2.2     | August 10, 2026    | October 10, 2027   |
| 2.1     | April 3, 2026      | June 3, 2027       |
| 2.0     | October 14, 2025   | December 14, 2026  |

Versions earlier than 2.0 are no longer supported.

## Check your data plane version

To see which chart version and app version a data plane runs, list your Helm releases.

```bash
helm list -n <NAMESPACE>
```

The `CHART` column shows the chart version, for example `airbyte-data-plane-2.5.0`, and the `APP VERSION` column shows the Airbyte version.

## Upgrade a data plane

To upgrade a data plane, update your Helm repository and redeploy the `airbyte-data-plane` chart with the new version and your existing values file. Use the same release name and namespace you used when you [deployed the data plane](data-plane#step-5).

```bash
helm repo update
helm upgrade --install <RELEASE_NAME> airbyte/airbyte-data-plane --version <NEW_VERSION> -n <NAMESPACE> --values values.yaml
```

You can browse all available chart versions on [Artifact Hub](https://artifacthub.io/packages/helm/airbyte/airbyte-data-plane).

If you need help planning or completing an upgrade, contact [Airbyte Support](https://support.airbyte.com/).
