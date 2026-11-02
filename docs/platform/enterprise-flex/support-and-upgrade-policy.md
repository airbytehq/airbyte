---
products: enterprise-flex
sidebar_label: Support and upgrade policy
---

# Enterprise Flex support and upgrade policy

In Enterprise Flex, Airbyte manages and upgrades the control plane and any Airbyte-managed data planes for you. You manage the self-managed data planes that run in your own infrastructure, including when you upgrade them. This policy explains how Airbyte releases new data plane versions, which versions Airbyte supports, and how often you need to upgrade.

This policy applies only to self-managed data planes you deploy with the `airbyte-data-plane` Helm chart.

## Release cadence

Airbyte releases a new minor version of its self-managed Helm charts, like 2.3 or 2.4, approximately every two months. Airbyte may also release patch versions, like 2.4.1, between minor versions to fix bugs and security issues.

Each version has [release notes](/release_notes/) that describe what's new and any action you need to take before you upgrade.

## Supported versions

Airbyte supports the three most recent minor versions of the data plane chart. When Airbyte releases a new minor version, the oldest of the three leaves the support window. For example, when Airbyte releases 2.5, 2.2 is no longer supported and the supported versions are 2.3, 2.4, and 2.5.

Within each supported minor version, Airbyte supports the latest patch version. If a fix you need is in a patch version, upgrade to that patch version.

If your data plane runs a version that Airbyte no longer supports, Airbyte Support may ask you to upgrade to a supported version before it can help you troubleshoot an issue.

## Breaking changes

Airbyte limits breaking changes to two releases per year. A breaking change is one that requires you to take action before or during an upgrade, like updating your `values.yaml` file, your Kubernetes resources, or your network configuration.

Airbyte documents breaking changes in the release notes for the version that introduces them and in the [breaking change list](/release_notes/self-managed/breaking-changes). If you skip versions when you upgrade, complete the steps for every version you skip.

## Your upgrade commitment

To stay within the support window, you commit to upgrading each of your self-managed data planes at least twice per year. Because Airbyte releases a new minor version approximately every two months, a data plane that you upgrade less often falls outside the support window.

Plan your upgrades as routine maintenance. Before each upgrade, review the release notes and the breaking change list for the versions you're upgrading through.

## Check your data plane version

To see which chart version and app version a data plane runs, list your Helm releases.

```bash
helm list -n <NAMESPACE>
```

The `CHART` column shows the chart version, for example `airbyte-data-plane-2.4.0`, and the `APP VERSION` column shows the Airbyte version.

## Upgrade a data plane

To upgrade a data plane, update your Helm repository and redeploy the `airbyte-data-plane` chart with the new version and your existing values file. Use the same release name and namespace you used when you [deployed the data plane](data-plane#step-5).

```bash
helm repo update
helm upgrade --install <RELEASE_NAME> airbyte/airbyte-data-plane --version <NEW_VERSION> -n <NAMESPACE> --values values.yaml
```

You can browse all available chart versions on [Artifact Hub](https://artifacthub.io/packages/helm/airbyte/airbyte-data-plane).

If you need help planning or completing an upgrade, contact [Airbyte Support](https://support.airbyte.com/).
