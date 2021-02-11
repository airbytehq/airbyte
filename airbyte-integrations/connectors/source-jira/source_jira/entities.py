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

# generated for keeping entities base params
ENTITIES_MAP = {
    "application_roles": {"url": "/applicationrole", "extractor": lambda v: v, "params": {}},
    "avatars": {"url": "/avatar/{type}/system", "extractor": lambda v: v["system"], "params": {}},
    "dashboards": {"url": "/dashboard", "extractor": lambda v: v["dashboards"], "params": {}},
    "filters": {"url": "/filter/search", "extractor": lambda v: v["values"], "params": {}},
    "filter_sharing": {"url": "/filter/{id}/permission", "extractor": lambda v: v, "params": {}},
    "groups": {"url": "/groups/picker", "extractor": lambda v: v["groups"], "params": {}},
    "issues": {
        "url": "/search",
        "extractor": lambda v: v["issues"],
        "params": {**{"fields": ["attachment", "issuelinks", "security", "issuetype"]}},
    },
    "issue_comments": {"url": "/issue/{key}/comment", "extractor": lambda v: v["comments"], "params": {}},
    "issue_fields": {"url": "/field", "extractor": lambda v: v, "params": {}},
    "issue_field_configurations": {"url": "/fieldconfiguration", "extractor": lambda v: v["values"], "params": {}},
    "issue_custom_field_contexts": {"url": "/field/{id}/context", "extractor": lambda v: v["values"], "params": {}},
    "issue_link_types": {"url": "/issueLinkType", "extractor": lambda v: v["issueLinkTypes"], "params": {}},
    "issue_navigator_settings": {"url": "/settings/columns", "extractor": lambda v: v, "params": {}},
    "issue_notification_schemes": {"url": "/notificationscheme", "extractor": lambda v: v["values"], "params": {}},
    "issue_priorities": {"url": "/priority", "extractor": lambda v: v, "params": {}},
    "issue_properties": {"url": "/issue/{issue_key}/properties/{property_key}", "extractor": lambda v: v, "params": {}},
    "issue_remote_links": {"url": "/issue/{key}/remotelink", "extractor": lambda v: v, "params": {}},
    "issue_resolutions": {"url": "/resolution", "extractor": lambda v: v, "params": {}},
    "issue_security_schemes": {"url": "/issuesecurityschemes", "extractor": lambda v: v["issueSecuritySchemes"], "params": {}},
    "issue_type_schemes": {"url": "/issuetypescheme", "extractor": lambda v: v["values"], "params": {}},
    "issue_type_screen_schemes": {"url": "/issuetypescreenscheme", "extractor": lambda v: v["values"], "params": {}},
    "issue_votes": {"url": "/issue/{key}/votes", "extractor": lambda v: v["voters"], "params": {}},
    "issue_watchers": {"url": "/issue/{key}/watchers", "extractor": lambda v: v["watchers"], "params": {}},
    "issue_worklogs": {"url": "/issue/{key}/worklog", "extractor": lambda v: v["worklogs"], "params": {}},
    "jira_settings": {"url": "/application-properties", "extractor": lambda v: v, "params": {}},
    "labels": {
        "url": "/label",
        "extractor": lambda v: [
            {"labels": v["values"]},
        ],
        "params": {},
    },
    "permissions": {
        "url": "/permissions",
        "extractor": lambda v: [
            v,
        ],
        "params": {},
    },
    "permission_schemes": {
        "url": "/permissionscheme",
        "extractor": lambda v: v["permissionSchemes"],
        "params": {},
    },
    "projects": {"url": "/project/search", "extractor": lambda v: v["values"], "params": {}},
    "project_avatars": {
        "url": "/project/{key}/avatars",
        "extractor": lambda v: [
            v,
        ],
        "params": {},
    },
    "project_categories": {"url": "/projectCategory", "extractor": lambda v: v, "params": {}},
    "project_components": {"url": "/project/{key}/component", "extractor": lambda v: v["values"], "params": {}},
    "project_email": {
        "url": "/project/{id}/email",
        "extractor": lambda v: [
            v,
        ],
        "params": {},
    },
    "project_permission_schemes": {
        "url": "/project/{key}/issuesecuritylevelscheme",
        "extractor": lambda v: [
            v,
        ],
        "params": {},
    },
    "project_types": {"url": "/project/type", "extractor": lambda v: v, "params": {}},
    "project_versions": {"url": "/project/{key}/version", "extractor": lambda v: v["values"], "params": {}},
    "screens": {"url": "/screens", "extractor": lambda v: v["values"], "params": {}},
    "screen_tabs": {"url": "/screens/{id}/tabs", "extractor": lambda v: v, "params": {}},
    "screen_tab_fields": {"url": "/screens/{id}/tabs/{tab_id}/fields", "extractor": lambda v: v, "params": {}},
    "screen_schemes": {"url": "/screenscheme", "extractor": lambda v: v["values"], "params": {}},
    "time_tracking": {"url": "/configuration/timetracking/list", "extractor": lambda v: v, "params": {}},
    "users": {"url": "/users/search", "extractor": lambda v: v, "params": {}},
    "workflows": {"url": "/workflow/search", "extractor": lambda v: v["values"], "params": {}},
    "workflow_transition_rules": {"url": "/workflow/search", "extractor": lambda v: v["values"], "params": {}},
    "workflow_schemes": {"url": "/workflowscheme", "extractor": lambda v: v["values"], "params": {}},
    "workflow_scheme_project_associations": {
        "url": "/workflowscheme/project",
        "extractor": lambda v: [
            v["values"],
        ],
        "params": {},
    },
    "workflow_statuses": {"url": "/status", "extractor": lambda v: v, "params": {}},
    "workflow_status_categories": {"url": "/statuscategory", "extractor": lambda v: v, "params": {}},
}
