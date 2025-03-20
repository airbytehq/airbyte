# Serpstat

This page contains the setup guide and reference information for the Serpstat source connector.

## Setup guide

### Step 1: Get Serpstat API key

#### For new Serpstat users

1. Create a new [Serpstat account](https://serpstat.com/signup/?utm_source=).
2. Go to [My account](https://serpstat.com/users/profile/) page and click **Get API key**.
3. Follow the instructions to get the API key.
4. Click **Copy** to copy the API key.

#### For existing Serpstat users

Go to [My account](https://serpstat.com/users/profile/) page and click **Copy** to copy the API key.

### Step 2: Set up the Serpstat connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up the source** page, select **Serpstat** from the **Source type** dropdown.
4. Enter a name for your connector.
5. Enter the API key.
6. Expand **Optional fields** and fill them in. Each API response consumes API credits available to your Serpstat subscription plan. To limit the number of consumed API rows, decrease **Page size** and **Pages to fetch** options.
7. Click **Set up source**.

## Supported sync modes

The Serpstat source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full refresh

## Supported Streams

- [Domains summary](https://serpstat.com/api/412-summarnij-otchet-po-domenu-v4-serpstatdomainproceduregetdomainsinfo/)
- [Domain history](https://serpstat.com/api/420-istoriya-po-domenu-v4-serpstatdomainproceduregetdomainshistory/)
- [Domain keywords](https://serpstat.com/api/584-top-search-engine-keywords-by-v4-domain-serpstatdomainproceduregetdomainkeywords/)
- [Domain keywords by region](https://serpstat.com/api/sorting-the-domain-by-keywords/)
- [Domain competitors](https://serpstat.com/api/590-domain-competitors-in-v4-search-result-serpstatdomainproceduregetcompetitors/)
- [Domain top pages](https://serpstat.com/api/588-domain-top-urls-v4-serpstatdomainproceduregettopurls/)

## Performance considerations

The maximum sync speed is limited by the number of requests per second per API key. See this limit in your [Serpstat account](https://serpstat.com/users/profile/).

## Changelog
<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                    |
| :------ | :--------- | :------------------------------------------------------- | :------------------------- |
| 0.2.15 | 2025-03-08 | [55081](https://github.com/airbytehq/airbyte/pull/55081) | Update dependencies |
| 0.2.14 | 2025-02-22 | [54485](https://github.com/airbytehq/airbyte/pull/54485) | Update dependencies |
| 0.2.13 | 2025-02-15 | [54094](https://github.com/airbytehq/airbyte/pull/54094) | Update dependencies |
| 0.2.12 | 2025-02-08 | [53475](https://github.com/airbytehq/airbyte/pull/53475) | Update dependencies |
| 0.2.11 | 2025-02-01 | [53021](https://github.com/airbytehq/airbyte/pull/53021) | Update dependencies |
| 0.2.10 | 2025-01-25 | [52522](https://github.com/airbytehq/airbyte/pull/52522) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51849](https://github.com/airbytehq/airbyte/pull/51849) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51306](https://github.com/airbytehq/airbyte/pull/51306) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50712](https://github.com/airbytehq/airbyte/pull/50712) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50230](https://github.com/airbytehq/airbyte/pull/50230) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49714](https://github.com/airbytehq/airbyte/pull/49714) | Update dependencies |
| 0.2.4 | 2024-12-12 | [48241](https://github.com/airbytehq/airbyte/pull/48241) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47928](https://github.com/airbytehq/airbyte/pull/47928) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47666](https://github.com/airbytehq/airbyte/pull/47666) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44067](https://github.com/airbytehq/airbyte/pull/44067) | Refactor connector to manifest-only format |
| 0.1.11 | 2024-08-12 | [43920](https://github.com/airbytehq/airbyte/pull/43920) | Update dependencies |
| 0.1.10 | 2024-08-10 | [43510](https://github.com/airbytehq/airbyte/pull/43510) | Update dependencies |
| 0.1.9 | 2024-08-03 | [43076](https://github.com/airbytehq/airbyte/pull/43076) | Update dependencies |
| 0.1.8 | 2024-07-27 | [42697](https://github.com/airbytehq/airbyte/pull/42697) | Update dependencies |
| 0.1.7 | 2024-07-20 | [42214](https://github.com/airbytehq/airbyte/pull/42214) | Update dependencies |
| 0.1.6 | 2024-07-13 | [41714](https://github.com/airbytehq/airbyte/pull/41714) | Update dependencies |
| 0.1.5 | 2024-07-10 | [41550](https://github.com/airbytehq/airbyte/pull/41550) | Update dependencies |
| 0.1.4 | 2024-07-06 | [40767](https://github.com/airbytehq/airbyte/pull/40767) | Update dependencies |
| 0.1.3 | 2024-06-25 | [40400](https://github.com/airbytehq/airbyte/pull/40400) | Update dependencies |
| 0.1.2 | 2024-06-23 | [40221](https://github.com/airbytehq/airbyte/pull/40221) | Update dependencies |
| 0.1.1 | 2024-05-30 | [38690](https://github.com/airbytehq/airbyte/pull/38690) | Make compatible with the builder |
| 0.1.0 | 2023-08-21 | [28147](https://github.com/airbytehq/airbyte/pull/28147) | Release Serpstat Connector |

</details>
