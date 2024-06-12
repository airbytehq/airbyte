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
| 0.2.5 | 2024-06-04 | [39093](https://github.com/airbytehq/airbyte/pull/39093) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.4 | 2024-05-28 | [38695](https://github.com/airbytehq/airbyte/pull/38695) | Make compatibility with builder |
| 0.2.3 | 2024-04-19 | [37267](https://github.com/airbytehq/airbyte/pull/37267) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37267](https://github.com/airbytehq/airbyte/pull/37267) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37267](https://github.com/airbytehq/airbyte/pull/37267) | schema descriptions |
| 0.2.0 | 2022-11-18 | [19143](https://github.com/airbytehq/airbyte/pull/19143) | Allow users to change base_url based on account's location |
| 0.1.0 | 2022-11-03 | [18395](https://github.com/airbytehq/airbyte/pull/18395) | Initial Release |
