# Spotify

Spotify Web API enables the retrieval of applications that can interact with Spotify's streaming service, such as retrieving content metadata, recommendations, playlists and playback.

The source connector fetches data from [Spotify Web API](https://developer.spotify.com/documentation/web-api)

## Prerequisites

- You own an Spotify developer account, free or paid.
- Follow the [Setup guide](#setup-guide) to authorize Airbyte to read data from your account.

## Setup guide

### Step 1: Set up an Spotify account

1. It's free to sign up an account in spotify.
2. Confirm your Email.
3. If you already have a bearer access token skip 2.1 else read 2.1

### Step 2.1: Create a new app for OAuth2

1. In Spotify developer console, go to [documentation](https://developer.spotify.com/documentation/web-api/concepts/apps). Create an app for getting the client credentails
2. Copy both **Client ID** and **Client Secret**.
3. In Airbyte, choose **OAuth2 Confidential application** under the **Authentication Method** menu, Paste the credentails
4. Click **Save** to test the connectivity.
5. More details can be found from [this documentation](https://developer.spotify.com/documentation/web-api).

### Step 2.2: Get an Access Tokens for Testing

1. To make calls for a production environment, you have setup an OAuth2 integration so that Airbyte can generate the access token automatically.
2. Else you are in a hurry you could use postman with Oauth2.0 with - base url as https://api.spotify.com/api/token and paste client id with client secret.
3. Set token name as any, grant type as Authorization code and check the 'Authorize using browser'
4. Set Auth url as https://accounts.spotify.com/authorize and Access token url as https://accounts.spotify.com/api/token.
5. Click on  the Get new access token and broser will redirect to spotify, don't forget to add the postman callback url while creating the app in spotify! else this won't work.
6. In Airbyte, choose **OAuth2 access token** under the **Authentication Method** menu, Paste the access token.
7. Click **Save** to test the connectivity.
8. More details can be found from [this documentation](https://developer.spotify.com/documentation/web-api).

## Supported sync modes

The Spotify source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Supported Streams

- [Current user profile](https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile)
- [User saved tracks](https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks)
- [Tracks recommendations](https://developer.spotify.com/documentation/web-api/reference/get-recommendations)
- [New releases](https://developer.spotify.com/documentation/web-api/reference/get-new-releases)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------- |
| 0.1.0   | 2023-11-21 | [-----](https://github.com/airbytehq/airbyte/pull/-----) | Add Spotify Source                                                      |