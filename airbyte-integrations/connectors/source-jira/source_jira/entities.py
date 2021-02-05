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
    "application_roles": {"url": "/applicationrole", "func": lambda v: v, "params": {}},
    "avatars": {"func": lambda v: v["system"], "params": {}},
    "dashboards": {"url": "/dashboard", "func": lambda v: v["dashboards"], "params": {}},
    "filters": {"url": "/filter/search", "func": lambda v: v["values"], "params": {}},
    "filter_sharing": {"func": lambda v: v, "params": {}},
    "groups": {"url": "/groups/picker", "func": lambda v: v["groups"], "params": {}},
    "issues": {
        "url": "/search",
        "func": lambda v: v["issues"],
        "params": {**{"fields": ["attachment", "issuelinks", "security", "issuetype"]}},
    },
    "issue_comments": {"func": lambda v: v["comments"], "params": {}},
    "issue_fields": {"url": "/field", "func": lambda v: v, "params": {}},
    "issue_field_configurations": {"url": "/fieldconfiguration", "func": lambda v: v["values"], "params": {}},
    "issue_custom_field_contexts": {"func": lambda v: v["values"], "params": {}},
    "issue_link_types": {"url": "/issueLinkType", "func": lambda v: v["issueLinkTypes"], "params": {}},
    "issue_navigator_settings": {"url": "/settings/columns", "func": lambda v: v, "params": {}},
    "issue_notification_schemes": {"url": "/notificationscheme", "func": lambda v: v["values"], "params": {}},
    "issue_priorities": {"url": "/priority", "func": lambda v: v, "params": {}},
    "issue_properties": {"func": lambda v: v["keys"], "params": {}},
    "issue_remote_links": {"func": lambda v: v, "params": {}},
    "issue_resolutions": {"url": "/resolution", "func": lambda v: v, "params": {}},
    "issue_security_schemes": {"url": "/issuesecurityschemes", "func": lambda v: v["issueSecuritySchemes"], "params": {}},
    "issue_type_schemes": {"url": "/issuetypescheme", "func": lambda v: v["values"], "params": {}},
    "issue_type_screen_schemes": {"url": "/issuetypescreenscheme", "func": lambda v: v["values"], "params": {}},
    "issue_votes": {"func": lambda v: v["voters"], "params": {}},
    "issue_watchers": {"func": lambda v: v["watchers"], "params": {}},
    "issue_worklogs": {"func": lambda v: v["worklogs"], "params": {}},
    "jira_settings": {"url": "/application-properties", "func": lambda v: v, "params": {}},
    "jql": {
        "url": "/jql/autocompletedata",
        "func": lambda v: [
            v,
        ],
        "params": {},
    },
    "labels": {
        "url": "/label",
        "func": lambda v: [
            {"labels": v["values"]},
        ],
        "params": {},
    },
    "permissions": {
        "url": "/permissions",
        "func": lambda v: [
            v,
        ],
        "params": {},
    },
    "permission_schemes": {
        "url": "/permissions",
        "func": lambda v: [
            v,
        ],
        "params": {},
    },
    "projects": {"url": "/project/search", "func": lambda v: v["values"], "params": {}},
    "project_avatars": {
        "func": lambda v: [
            v,
        ],
        "params": {},
    },
    "project_categories": {"url": "/projectCategory", "func": lambda v: v, "params": {}},
    "project_components": {"func": lambda v: v["values"], "params": {}},
    "project_email": {
        "func": lambda v: [
            v,
        ],
        "params": {},
    },
    "project_permission_schemes": {
        "func": lambda v: [
            v,
        ],
        "params": {},
    },
    "project_types": {"url": "/project/type", "func": lambda v: v, "params": {}},
    "project_versions": {"func": lambda v: v["values"], "params": {}},
    "screens": {"url": "/screens", "func": lambda v: v["values"], "params": {}},
    "screen_tabs": {"func": lambda v: v, "params": {}},
    "screen_tab_fields": {"func": lambda v: v, "params": {}},
    "screen_schemes": {"url": "/screenscheme", "func": lambda v: v["values"], "params": {}},
    "server_info": {
        "url": "/serverInfo",
        "func": lambda v: [
            v,
        ],
        "params": {},
    },
    "time_tracking": {"url": "/configuration/timetracking/list", "func": lambda v: v, "params": {}},
    "users": {"url": "/users/search", "func": lambda v: v, "params": {}},
    "workflows": {"url": "/workflow/search", "func": lambda v: v["values"], "params": {}},
    "workflow_transition_rules": {"url": "/workflow/search", "func": lambda v: v["values"], "params": {}},
    "workflow_schemes": {"url": "/workflowscheme", "func": lambda v: v["values"], "params": {}},
    "workflow_scheme_project_associations": {
        "url": "/workflowscheme/project",
        "func": lambda v: [
            v["values"],
        ],
        "params": {},
    },
    "workflow_scheme_drafts": {"func": lambda v: v, "params": {}},
    "workflow_statuses": {"url": "/status", "func": lambda v: v, "params": {}},
    "workflow_status_categories": {"url": "/statuscategory", "func": lambda v: v, "params": {}},
}
