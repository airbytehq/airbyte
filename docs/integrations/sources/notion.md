# Notion

## Overview

Notion is a productivity and project management software. It was designed to help organizations coordinate deadlines, objectives, and assignments.

## Setup Guide

### For Airbyte OSS:

1. Login to your Notion account and go to https://www.notion.so/my-integrations.
2. Create a new integration. Make sure to check the `Read content` capability.
3. Check the appropriate user capability depending on your use case.
4. Click `Submit`.
5. Copy the access token from the next screen.
6. On Airbyte, go to the sources option on the left and click the `+ New source` option.
7. Select the Notion source and provide the start date.
8. Paste the access token from the Notion integration page.
9. Click the `Setup source` button. You should be able to start getting data.


## Connector Reference

### Supported features
| Feature | Supported? | Notes
| :--- | :--- | :---
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes | Not supported for `Users` stream
| SSL connection | Yes |
| Namespaces | No |

### Output schema

This Source is capable of syncing the following core streams:

| Stream name                  | Schema |
|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Blocks             | `{"object":"block","id":"50a5304c-db79-4ff0-be31-1d92e7329b5b","created_time":"2022-03-29T02:35:00.000Z","last_edited_time":"2022-03-29T02:35:00.000Z","created_by":{"object":"user","id":"8e308f26-bc66-434b-b126-ed666a3c30fc"},"last_edited_by":{"object":"user","id":"8e308f26-bc66-434b-b126-ed666a3c30fc"},"has_children":false,"archived":false,"type":"quote","quote":{"color":"default","text":[{"type":"text","text":{"content":"This is a quote","link":null},"annotations":{"bold":false,"italic":false,"strikethrough":false,"underline":false,"code":false,"color":"default"},"plain_text":"This is a quote","href":null}]}}` |
| Databases              | `{"object":"database","id":"3b3d40b6-9ef9-495b-8317-db33cb913999","cover":null,"icon":{"type":"emoji","emoji":"♠️"},"created_time":"2022-03-26T23:52:00.000Z","created_by":{"object":"user","id":"8e308f26-bc66-434b-b126-ed666a3c30fc"},"last_edited_by":{"object":"user","id":"8e308f26-bc66-434b-b126-ed666a3c30fc"},"last_edited_time":"2022-03-29T02:29:00.000Z","title":[{"type":"text","text":{"content":"My Database","link":null},"annotations":{"bold":false,"italic":false,"strikethrough":false,"underline":false,"code":false,"color":"default"},"plain_text":"My Database","href":null}],"properties":{"Value Column":{"id":"fvtR","name":"Value Column","type":"rich_text","rich_text":{}},"Tags":{"id":"l%3Emj","name":"Tags","type":"multi_select","multi_select":{"options":[{"id":"5e942851-00ed-4a1b-af6a-1e1a73c6873b","name":"awesome","color":"blue"},{"id":"6924c772-0662-4132-a0a5-614161021691","name":"airbyte","color":"gray"}]}},"Date column":{"id":"%7Cz%3D~","name":"Date column","type":"date","date":{}},"Name":{"id":"title","name":"Name","type":"title","title":{}}},"parent":{"type":"workspace","workspace":true},"url":"https://www.notion.so/3b3d40b69ef9495b8317db33cb913999","archived":false}` |
| Pages                        | `{"object":"page","id":"f309eed2-9c54-4e89-8d2e-947c18462c85","created_time":"2022-03-27T02:10:00.000Z","last_edited_time":"2022-03-29T02:34:00.000Z","created_by":{"object":"user","id":"8e308f26-bc66-434b-b126-ed666a3c30fc"},"last_edited_by":{"object":"user","id":"8e308f26-bc66-434b-b126-ed666a3c30fc"},"cover":null,"icon":{"type":"emoji","emoji":"📎"},"parent":{"type":"workspace","workspace":true},"archived":false,"properties":{"title":{"id":"title","type":"title","title":[{"type":"text","text":{"content":"My sample page","link":null},"annotations":{"bold":false,"italic":false,"strikethrough":false,"underline":false,"code":false,"color":"default"},"plain_text":"My sample page","href":null}]}},"url":"https://www.notion.so/My-sample-page-f309eed29c544e898d2e947c18462c85"}` |
| Users                    | `{"object":"user","id":"8e308f26-bc66-434b-b126-ed666a3c30fc","name":"John Doe","avatar_url":"https://host.com/profile-notion.jpg","type":"person","person":{"email":"john.doe@company.io"}}` |


The `Databases` and `Pages` streams are using same `Search` endpoint.

Notion stores `Blocks` in hierarchical structure, so we use recursive request to get list of blocks.


### Performance considerations

The connector is restricted by normal Notion [rate limits and size limits](https://developers.notion.com/reference/errors#request-limits).

The Notion connector should not run into Notion API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

### Sync considerations

In order for your connection to successfully sync the pages and blocks you expect, you should share the corresponding pages with your Notion integration first. That also applies to child pages. You won't be able to see blocks from child pages if you explicitly don't share them with your integration.


## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.3 | 2022-04-22 | [11452](https://github.com/airbytehq/airbyte/pull/11452) | Use pagination for User stream |
| 0.1.2 | 2022-01-11 | [9084](https://github.com/airbytehq/airbyte/pull/9084) | Fix documentation URL |
| 0.1.1 | 2021-12-30 | [9207](https://github.com/airbytehq/airbyte/pull/9207) | Update connector fields title/description |
| 0.1.0 | 2021-10-17 | [7092](https://github.com/airbytehq/airbyte/pull/7092) | Initial Release |


