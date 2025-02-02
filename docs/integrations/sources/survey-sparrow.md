# SurveySparrow

This page guides you through the process of setting up the SurveySparrow source connector.

## Prerequisites

### For Airbyte Open Source:

- Access Token

## Setup guide

### Step 1: Set up SurveySparrow

Please read this [docs](https://developers.surveysparrow.com/rest-apis).

In order to get access token, follow these steps:

1. Login to your surveysparrow account and go to Settings → Apps & Integrations
2. Create a Private App
3. Enter Name, Description, select scope and generate the access token
4. Copy and keep the access token in a safe place (Access token will be displayed only once and you may need to re-generate if you misplaced)
5. Save your app and you are good to start developing your private app

## Step 2: Set up the source connector in Airbyte

**For Airbyte Open Source:**

1. Go to local Airbyte page
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**
3. On the source setup page, select **SurveySparrow** from the Source type dropdown and enter a name for this connector
4. Add **Access Token**
5. Select whether SurveySparrow account location is EU-based
6. Add Survey ID (optional)
7. Click `Set up source`

## Supported streams and sync modes

- [Contacts](https://developers.surveysparrow.com/rest-apis/contacts#getV3Contacts)
- [ContactLists](https://developers.surveysparrow.com/rest-apis/contact_lists#getV3Contact_lists)
- [Questions](https://developers.surveysparrow.com/rest-apis/questions#getV3Questions)
- [Responses](https://developers.surveysparrow.com/rest-apis/response#getV3Responses)
- [Roles](https://developers.surveysparrow.com/rest-apis/roles#getV3Roles)
- [Surveys](https://developers.surveysparrow.com/rest-apis/survey#getV3Surveys)
- [SurveyFolders](https://developers.surveysparrow.com/rest-apis/survey_folder#getV3Survey_folders)
- [Users](https://developers.surveysparrow.com/rest-apis/users#getV3Users)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.10 | 2025-02-01 | [53056](https://github.com/airbytehq/airbyte/pull/53056) | Update dependencies |
| 0.3.9 | 2025-01-25 | [52442](https://github.com/airbytehq/airbyte/pull/52442) | Update dependencies |
| 0.3.8 | 2025-01-18 | [51972](https://github.com/airbytehq/airbyte/pull/51972) | Update dependencies |
| 0.3.7 | 2025-01-11 | [51404](https://github.com/airbytehq/airbyte/pull/51404) | Update dependencies |
| 0.3.6 | 2024-12-28 | [50824](https://github.com/airbytehq/airbyte/pull/50824) | Update dependencies |
| 0.3.5 | 2024-12-21 | [50355](https://github.com/airbytehq/airbyte/pull/50355) | Update dependencies |
| 0.3.4 | 2024-12-14 | [49766](https://github.com/airbytehq/airbyte/pull/49766) | Update dependencies |
| 0.3.3 | 2024-12-12 | [48163](https://github.com/airbytehq/airbyte/pull/48163) | Update dependencies |
| 0.3.2 | 2024-10-28 | [47506](https://github.com/airbytehq/airbyte/pull/47506) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-14 | [44059](https://github.com/airbytehq/airbyte/pull/44059) | Refactor connector to manifest-only format |
| 0.2.14 | 2024-08-10 | [43652](https://github.com/airbytehq/airbyte/pull/43652) | Update dependencies |
| 0.2.13 | 2024-08-03 | [43147](https://github.com/airbytehq/airbyte/pull/43147) | Update dependencies |
| 0.2.12 | 2024-07-27 | [42303](https://github.com/airbytehq/airbyte/pull/42303) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41924](https://github.com/airbytehq/airbyte/pull/41924) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41556](https://github.com/airbytehq/airbyte/pull/41556) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41172](https://github.com/airbytehq/airbyte/pull/41172) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40975](https://github.com/airbytehq/airbyte/pull/40975) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40481](https://github.com/airbytehq/airbyte/pull/40481) | Update dependencies |
| 0.2.6 | 2024-06-22 | [40064](https://github.com/airbytehq/airbyte/pull/40064) | Update dependencies |
| 0.2.5 | 2024-06-04 | [39093](https://github.com/airbytehq/airbyte/pull/39093) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.4 | 2024-05-28 | [38695](https://github.com/airbytehq/airbyte/pull/38695) | Make compatibility with builder |
| 0.2.3 | 2024-04-19 | [37267](https://github.com/airbytehq/airbyte/pull/37267) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37267](https://github.com/airbytehq/airbyte/pull/37267) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37267](https://github.com/airbytehq/airbyte/pull/37267) | schema descriptions |
| 0.2.0 | 2022-11-18 | [19143](https://github.com/airbytehq/airbyte/pull/19143) | Allow users to change base_url based on account's location |
| 0.1.0 | 2022-11-03 | [18395](https://github.com/airbytehq/airbyte/pull/18395) | Initial Release |
