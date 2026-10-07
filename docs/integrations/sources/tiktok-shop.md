# TikTok Shop

## Overview

The TikTok Shop source supports Full Refresh syncs for all endpoints.

### Available streams

Several output streams are available from this source:

- [active shops](https://partner.tiktokshop.com/docv2/page/650a69e24a0bb702c067291c?external_id=650a69e24a0bb702c067291c)
- [brands](https://partner.tiktokshop.com/docv2/page/6503075656e2bb0289dd5d01?external_id=6503075656e2bb0289dd5d01)
- [categories](https://partner.tiktokshop.com/docv2/page/6509c89d0fcef602bf1acd9b?external_id=6509c89d0fcef602bf1acd9b)
- [category rules](https://partner.tiktokshop.com/docv2/page/6509c0febace3e02b74594a9?external_id=6509c0febace3e02b74594a9)
- [attributes](https://partner.tiktokshop.com/docv2/page/6509c5784a0bb702c0561cc8?external_id=6509c5784a0bb702c0561cc8)
- [products](https://partner.tiktokshop.com/docv2/page/6509d85b4a0bb702c057fdda?external_id=6509d85b4a0bb702c057fdda)
- [listing schemas](https://partner.tiktokshop.com/docv2/page/6694e57cde15e502ed0a1b2d?external_id=6694e57cde15e502ed0a1b2d)
- [order detail](https://partner.tiktokshop.com/docv2/page/650aa8ccc16ffe02b8f167a0?external_id=650aa8ccc16ffe02b8f167a0)
- [package detail](https://partner.tiktokshop.com/docv2/page/650aa39fbace3e02b75d8617?external_id=650aa39fbace3e02b75d8617)

If there are more streams you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                               | Supported? |
| :----------------------------         | :--------- |
| Full Refresh Sync                     | Yes        |
| Incremental Sync                      | No         |
| Replicate Incremental Deletes         | No         |
| Namespaces                            | No         |
| Localization (Multiple Languages)     | Yes        |

### Performance considerations

The TikTok Shop connector should not run into TikTok Shop API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- TikTok Shop App Key
- Start date
- End date

### Setup guide

Please follow the [TikTok Shop documentation for retrieving the app key](https://partner.tiktokshop.com/docv2/page/64f1994264ed2e0295f3d631).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------ |
| 0.1.0   | 2024-08-28 | [x](https://github.com/airbytehq/airbyte/pull/x)         | Initial release                             |

</details>
