---
dockerRepository: airbyte/destination-hubspot
---

# HubSpot Destination

This page guides you through the process of setting up the [HubSpot](https://www.hubspot.com/) destination connector. This connector supports [data activation](/platform/move-data/elt-data-activation) for operational workflows.

## Prerequisites

- A HubSpot account
- Airbyte version 1.8 or later, or Airbyte Cloud

### S3 prerequisites for rejected records

If you're using an S3 bucket to store rejected records, you also need the following.

1. Allow connections from Airbyte to your AWS S3/Minio S3 cluster (if they exist in separate VPCs).
2. [Enforce encryption of data in transit](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html#transit).
3. An S3 bucket with credentials, a Role ARN, or an instance profile with read/write permissions configured for the host (EC2, EKS).

    - These fields are always required:

      - **S3 Bucket Name**
      - **S3 Bucket Region**
      - **Prefix Path in the Bucket**

    - If you are using STS Assume Role, you must provide:

      - **Role ARN**

    - If you are using AWS credentials, you must provide:

      - **Access Key ID**
      - **Secret Access Key**

    - If you are using an Instance Profile, you may omit the Access Key ID, Secret Access Key, and Role ARN.

## Setup guide

### Set up the HubSpot connector in Airbyte

1. Log into your Airbyte account.
2. Click Destination and then click + New destination.
3. On the Set up the destination page, select HubSpot from the Destination tiles.
4. Enter a name for the HubSpot connector.
5. From the **Authentication** dropdown, OAuth authentication is available so click **Authenticate your HubSpot account** to sign in with HubSpot and authorize your account.

   :::note HubSpot Authentication issues
   You may encounter an error during the authentication process in the popup window with the message `An invalid scope name was provided`. To resolve this, close the window and retry authentication.
   :::

6. Click **Set up destination** and wait for the tests to complete.

## Supported Objects

The HubSpot destination connector supports the following streams:

- [Companies](https://developers.hubspot.com/docs/api/crm/companies): Upsert on unique field
- [Contacts](https://developers.hubspot.com/docs/methods/contacts): Upsert on email
- [Deals](https://developers.hubspot.com/docs/api/crm/deals): Upsert on unique field
- [Custom Objects](https://developers.hubspot.com/docs/guides/api/crm/objects/custom-objects): Upsert on unique field

## Limitations & Troubleshooting

### Rate Limiting

The connector automatically respects HubSpot's standard API rate limits. If you encounter rate limiting issues, the connector will retry requests with exponential backoff.

### Destination Object Not Showing Up

Except for the CONTACT object (which uses email as the matching key), the upsert method for this connector requires a unique value field to be present on the destination object.

**Matching Key Requirements:**
- **CONTACT**: Uses email field automatically
- **All other objects**: Require a property with unique values enabled

To create a unique value property in HubSpot:
* In the CRM menu in the left-hand side, select the object you want to sync
* Under `Actions`, select `Edit Properties`
* Click on `Create property`
* When entering the rules, check `Require unique values for this property`


### App Verification

In order to verify our HubSpot application, HubSpot expects some usage i.e. [more than 60 installations](https://developers.hubspot.com/docs/guides/apps/marketplace/certification-requirements#value). Hence, when installing the app, you might see the message "You're connecting to an unverified app". This is expected for our first users. Once we have enough traffic on the application, we will be able to verify the app which will remove this warning.

### Scopes for Unsupported Streams

During app the app installation, you might see scopes related to objects we don't support. This is expected as changing scopes might require the users to re-authenticate which is quite disruptive. In order to prevent that, we added scopes on objects we intend to support given user demands.

### 403 Forbidden Error

Hubspot has **scopes** for each API call. Each stream is tied to a scope and will need access to that scope to sync data. Review the Hubspot OAuth scope documentation [here](https://developers.hubspot.com/docs/api/working-with-oauth#scopes).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                    | Subject                                   |
|:--------|:-----------|:----------------------------------------------------------------|:------------------------------------------|
| 0.0.8 | 2025-11-01 | [69131](https://github.com/airbytehq/airbyte/pull/69131) | Upgrade to Bulk CDK 0.1.61. |
| 0.0.7   | 2025-09-24 | [66684](https://github.com/airbytehq/airbyte/pull/66684)        | Pin to CDK artifact                       |
| 0.0.6   | 2025-09-09 | [65986](https://github.com/airbytehq/airbyte/pull/65986)        | Adding product object                     |
| 0.0.5   | 2025-09-08 | [65157](https://github.com/airbytehq/airbyte/pull/65157)        | Update following breaking changes on spec |
| 0.0.4   | 2025-08-01 | [64144](https://github.com/airbytehq/airbyte/pull/64144)        | OSS release                               |
| 0.0.3   | 2025-07-18 | [205](https://github.com/airbytehq/airbyte-enterprise/pull/205) | Forcing new release                       |
| 0.0.2   | 2025-07-18 | [204](https://github.com/airbytehq/airbyte-enterprise/pull/204) | Fixing auth                               |
| 0.0.1   | 2025-07-18 | [201](https://github.com/airbytehq/airbyte-enterprise/pull/201) | First iteration internally                |

</details>
