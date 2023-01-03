# RD Station Marketing

## Overview

RD Station Marketing is the leading Marketing Automation tool in Latin America. It is a software application that helps your company carry out better campaigns, nurture Leads, generate qualified business opportunities and achieve more results. From social media to email, Landing Pages, Pop-ups, even Automations and Analytics.

## Authentication

RD Station Marketing uses Oauth2 to authenticate. To get the credentials, you need first to create an App for private use in this [link](https://appstore.rdstation.com/en/publisher) (needs to be loged in to access). After that, follow [these](https://developers.rdstation.com/reference/autenticacao?lng=en) instructions to create the client_id and client_secret.

## Endpoints

There are eleven endpoints in RD Station Marketing Connector:

- [Analytics Conversions](https://developers.rdstation.com/reference/get_platform-analytics-conversions?lng=en): Responds with conversion statistics for campaings and other marketing assets.
- [Analytics Emails](https://developers.rdstation.com/reference/get_platform-analytics-emails?lng=en): Responds with statistics about the emails sent with this tool.
- [Analytics Funnel](https://developers.rdstation.com/reference/get_platform-analytics-funnel): Responds with the sales funnel for a given period, grouped by day.
- [Analytics Workflow Emails Statistics](https://developers.rdstation.com/reference/get_platform-analytics-workflow-emails): Responds with statistics about emails sent via an automation flow.
- [Emails](https://developers.rdstation.com/reference/get_platform-emails): List all sent emails.
- [Embeddables](https://developers.rdstation.com/reference/get_platform-embeddables): Returns a list of all forms for an account.
- [Fields](https://developers.rdstation.com/reference/get_platform-contacts-fields): Returns all fields, customized and default, and its attributes.
- [Landing Pages](https://developers.rdstation.com/reference/get_platform-landing-pages): Returns a list of all landing pages for an account.
- [Pop-ups](https://developers.rdstation.com/reference/get_platform-popups): Returns a list of all pop-ups for an account.
- [Segmentations](https://developers.rdstation.com/reference/get_platform-segmentations): List all segmentations, custom and default.
- [Workflows](https://developers.rdstation.com/reference/get_platform-workflows): Returns all automation flows.

## Quick Notes

- The analytics streams are only supported if you have a Pro or Enterprise RD Station Account. The usage is available only to these plans.
