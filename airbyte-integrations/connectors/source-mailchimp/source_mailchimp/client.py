"""
MIT License
Copyright (c) 2020 Airbyte
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from airbyte_protocol import AirbyteStream
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

from .models import HealthCheckError


class Client:
    def __init__(self, username: str, apikey: str):
        self._client = MailChimp(mc_api=apikey, mc_user=username)

        """ TODO:
        Authorized Apps
        Automations
        Campaign Folders
        Campaigns
        Chimp Chatter Activity
        Connected Sites
        Conversations
        E-Commerce Stores
        Facebook Ads
        Files
        Landing Pages
        Lists
        Ping
        Reports
        """

    def health_check(self):
        try:
            self._client.ping.get()
            return True, None
        except MailChimpError as err:
            return False, HealthCheckError.parse_obj(err.args[0])

    def lists_stream(self):
        self._client.lists.all(count=1)

        # TODO
        json_schema = {
            "$ref": "https://us2.api.mailchimp.com/schema/3.0/Definitions/Lists/Response.json",
        }

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Subscriber List",
            "description": "Information about a specific list.",
            "properties": {
                "id": {
                    "type": "string",
                    "title": "List ID",
                    "description": "A string that uniquely identifies this list.",
                    "readOnly": True
                },
                "web_id": {
                    "type": "integer",
                    "title": "List Web ID",
                    "description": "The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https://{dc}.admin.mailchimp.com/lists/members/?id={web_id}`.",
                    "readOnly": True
                },
                "name": {
                    "type": "string",
                    "title": "List Name",
                    "description": "The name of the list."
                },
                "contact": {
                    "type": "object",
                    "title": "List Contact",
                    "description": "[Contact information displayed in campaign footers](https://mailchimp.com/help/about-campaign-footers/) to comply with international spam laws.",
                    "properties": {
                        "company": {
                            "type": "string",
                            "title": "Company Name",
                            "description": "The company name for the list."
                        },
                        "address1": {
                            "type": "string",
                            "title": "Address",
                            "description": "The street address for the list contact."
                        },
                        "address2": {
                            "type": "string",
                            "title": "Address",
                            "description": "The street address for the list contact."
                        },
                        "city": {
                            "type": "string",
                            "title": "City",
                            "description": "The city for the list contact."
                        },
                        "state": {
                            "type": "string",
                            "title": "State",
                            "description": "The state for the list contact."
                        },
                        "zip": {
                            "type": "string",
                            "title": "Postal Code",
                            "description": "The postal or zip code for the list contact."
                        },
                        "country": {
                            "type": "string",
                            "title": "Country Code",
                            "description": "A two-character ISO3166 country code. Defaults to US if invalid."
                        },
                        "phone": {
                            "type": "string",
                            "title": "Phone Number",
                            "description": "The phone number for the list contact."
                        }
                    }
                },
                "permission_reminder": {
                    "type": "string",
                    "title": "Permission Reminder",
                    "description": "The [permission reminder](https://mailchimp.com/help/edit-the-permission-reminder/) for the list."
                },
                "use_archive_bar": {
                    "type": "boolean",
                    "title": "Use Archive Bar",
                    "description": "Whether campaigns for this list use the [Archive Bar](https://mailchimp.com/help/about-email-campaign-archives-and-pages/) in archives by default.",
                    "default": False
                },
                "campaign_defaults": {
                    "type": "object",
                    "title": "Campaign Defaults",
                    "description": "[Default values for campaigns](https://mailchimp.com/help/edit-your-emails-subject-preview-text-from-name-or-from-email-address/) created for this list.",
                    "properties": {
                        "from_name": {
                            "type": "string",
                            "title": "Sender's Name",
                            "description": "The default from name for campaigns sent to this list."
                        },
                        "from_email": {
                            "type": "string",
                            "title": "Sender's Email Address",
                            "description": "The default from email for campaigns sent to this list."
                        },
                        "subject": {
                            "type": "string",
                            "title": "Subject",
                            "description": "The default subject line for campaigns sent to this list."
                        },
                        "language": {
                            "type": "string",
                            "title": "Language",
                            "description": "The default language for this lists's forms."
                        }
                    }
                },
                "notify_on_subscribe": {
                    "type": "string",
                    "title": "Notify on Subscribe",
                    "description": "The email address to send [subscribe notifications](https://mailchimp.com/help/change-subscribe-and-unsubscribe-notifications/) to.",
                    "default": False
                },
                "notify_on_unsubscribe": {
                    "type": "string",
                    "title": "Notify on Unsubscribe",
                    "description": "The email address to send [unsubscribe notifications](https://mailchimp.com/help/change-subscribe-and-unsubscribe-notifications/) to.",
                    "default": False
                },
                "date_created": {
                    "type": "string",
                    "title": "Creation Date",
                    "description": "The date and time that this list was created in ISO 8601 format.",
                    "format": "date-time",
                    "readOnly": True
                },
                "list_rating": {
                    "type": "integer",
                    "title": "List Rating",
                    "description": "An auto-generated activity score for the list (0-5).",
                    "readOnly": True
                },
                "email_type_option": {
                    "type": "boolean",
                    "title": "Email Type Option",
                    "description": "Whether the list supports [multiple formats for emails](https://mailchimp.com/help/change-list-name-and-defaults/). When set to `True`, subscribers can choose whether they want to receive HTML or plain-text emails. When set to `False`, subscribers will receive HTML emails, with a plain-text alternative backup."
                },
                "subscribe_url_short": {
                    "type": "string",
                    "title": "Subscribe URL Short",
                    "description": "Our [EepURL shortened](https://mailchimp.com/help/share-your-signup-form/) version of this list's subscribe form.",
                    "readOnly": True
                },
                "subscribe_url_long": {
                    "type": "string",
                    "title": "Subscribe URL Long",
                    "description": "The full version of this list's subscribe form (host will vary).",
                    "readOnly": True
                },
                "beamer_address": {
                    "type": "string",
                    "title": "Beamer Address",
                    "description": "The list's [Email Beamer](https://mailchimp.com/help/use-email-beamer-to-create-a-campaign/) address.",
                    "readOnly": True
                },
                "visibility": {
                    "type": "string",
                    "title": "Visibility",
                    "enum": [
                        "pub",
                        "prv"
                    ],
                    "description": "Whether this list is [public or private](https://mailchimp.com/help/about-list-publicity/)."
                },
                "double_optin": {
                    "type": "boolean",
                    "title": "Double Opt In",
                    "description": "Whether or not to require the subscriber to confirm subscription via email.",
                    "default": False
                },
                "has_welcome": {
                    "type": "boolean",
                    "title": "Has Welcome",
                    "description": "Whether or not this list has a welcome automation connected. Welcome Automations: welcomeSeries, singleWelcome, emailFollowup.",
                    "default": False,
                    "example": False
                },
                "marketing_permissions": {
                    "type": "boolean",
                    "title": "Marketing Permissions",
                    "description": "Whether or not the list has marketing permissions (eg. GDPR) enabled.",
                    "default": False
                },
                "modules": {
                    "type": "array",
                    "title": "Modules",
                    "description": "Any list-specific modules installed for this list.",
                    "items": {
                        "type": "string"
                    },
                    "readOnly": True
                },
                "stats": {
                    "type": "object",
                    "title": "Statistics",
                    "description": "Stats for the list. Many of these are cached for at least five minutes.",
                    "readOnly": True,
                    "properties": {
                        "member_count": {
                            "type": "integer",
                            "title": "Member Count",
                            "description": "The number of active members in the list.",
                            "readOnly": True
                        },
                        "total_contacts": {
                            "type": "integer",
                            "title": "Total Contacts",
                            "description": "The number of contacts in the list, including subscribed, unsubscribed, pending, cleaned, deleted, transactional, and those that need to be reconfirmed.",
                            "readOnly": True
                        },
                        "unsubscribe_count": {
                            "type": "integer",
                            "title": "Unsubscribe Count",
                            "description": "The number of members who have unsubscribed from the list.",
                            "readOnly": True
                        },
                        "cleaned_count": {
                            "type": "integer",
                            "title": "Cleaned Count",
                            "description": "The number of members cleaned from the list.",
                            "readOnly": True
                        },
                        "member_count_since_send": {
                            "type": "integer",
                            "title": "Member Count Since Send",
                            "description": "The number of active members in the list since the last campaign was sent.",
                            "readOnly": True
                        },
                        "unsubscribe_count_since_send": {
                            "type": "integer",
                            "title": "Unsubscribe Count Since Send",
                            "description": "The number of members who have unsubscribed since the last campaign was sent.",
                            "readOnly": True
                        },
                        "cleaned_count_since_send": {
                            "type": "integer",
                            "title": "Cleaned Count Since Send",
                            "description": "The number of members cleaned from the list since the last campaign was sent.",
                            "readOnly": True
                        },
                        "campaign_count": {
                            "type": "integer",
                            "title": "Campaign Count",
                            "description": "The number of campaigns in any status that use this list.",
                            "readOnly": True
                        },
                        "campaign_last_sent": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Campaign Last Sent",
                            "description": "The date and time the last campaign was sent to this list in ISO 8601 format. This is updated when a campaign is sent to 10 or more recipients.",
                            "readOnly": True
                        },
                        "merge_field_count": {
                            "type": "integer",
                            "title": "Merge Var Count",
                            "description": "The number of merge vars for this list (not EMAIL, which is required).",
                            "readOnly": True
                        },
                        "avg_sub_rate": {
                            "type": "number",
                            "title": "Average Subscription Rate",
                            "description": "The average number of subscriptions per month for the list (not returned if we haven't calculated it yet).",
                            "readOnly": True
                        },
                        "avg_unsub_rate": {
                            "type": "number",
                            "title": "Average Unsubscription Rate",
                            "description": "The average number of unsubscriptions per month for the list (not returned if we haven't calculated it yet).",
                            "readOnly": True
                        },
                        "target_sub_rate": {
                            "type": "number",
                            "title": "Average Subscription Rate",
                            "description": "The target number of subscriptions per month for the list to keep it growing (not returned if we haven't calculated it yet).",
                            "readOnly": True
                        },
                        "open_rate": {
                            "type": "number",
                            "title": "Open Rate",
                            "description": "The average open rate (a percentage represented as a number between 0 and 100) per campaign for the list (not returned if we haven't calculated it yet).",
                            "readOnly": True
                        },
                        "click_rate": {
                            "type": "number",
                            "title": "Click Rate",
                            "description": "The average click rate (a percentage represented as a number between 0 and 100) per campaign for the list (not returned if we haven't calculated it yet).",
                            "readOnly": True
                        },
                        "last_sub_date": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Date of Last List Subscribe",
                            "description": "The date and time of the last time someone subscribed to this list in ISO 8601 format.",
                            "readOnly": True
                        },
                        "last_unsub_date": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Date of Last List Unsubscribe",
                            "description": "The date and time of the last time someone unsubscribed from this list in ISO 8601 format.",
                            "readOnly": True
                        }
                    }
                },
                "_links": {
                    "$ref": "https://us2.api.mailchimp.com/schema/3.0/Definitions/HATEOASLinks.json"
                }
            }
        }

        return AirbyteStream(name='Lists', json_schema=json_schema)

    def lists(self):
        return self._client.lists.all()['lists']
