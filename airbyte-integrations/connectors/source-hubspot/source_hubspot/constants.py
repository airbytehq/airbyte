#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

OAUTH_CREDENTIALS = "OAuth Credentials"
PRIVATE_APP_CREDENTIALS = "Private App Credentials"

# set of standard stream names to check for custom object name collisions
STANDARD_STREAM_NAMES = {
    "campaigns",
    "companies",
    "contact_lists",
    "contacts",
    "contacts_form_submissions",
    "contacts_list_memberships",
    "contacts_merged_audit",
    "deal_pipelines",
    "deals",
    "deals_archived",
    "email_events",
    "email_subscriptions",
    "engagements",
    "engagements_calls",
    "engagements_emails",
    "engagements_meetings",
    "engagements_notes",
    "engagements_tasks",
    "forms",
    "form_submissions",
    "goals",
    "line_items",
    "marketing_emails",
    "owners",
    "owners_archived",
    "products",
    "contacts_property_history",
    "companies_property_history",
    "deals_property_history",
    "subscription_changes",
    "tickets",
    "ticket_pipelines",
    "workflows",
}
