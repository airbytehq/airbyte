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

from dashboards import Dashboards
from filter_sharing import FilterSharing
from filters import Filters
from groups import Groups
from issue_attachments import IssueAttachments
from issue_comments import IssueComments
from issue_fields import IssueFields
from issue_links import IssueLinks
from issue_remote_links import IssueRemoteLinks
from issue_votes import IssueVotes
from issue_watchers import IssueWatchers
from issue_worklogs import IssueWorklogs
from issues import Issues
from project_categories import ProjectCategories
from project_components import ProjectComponents
from project_roles import ProjectRoles
from project_versions import ProjectVersions
from projects import Projects
from screens import Screens
from users import Users
from workflow_schemes import WorkflowSchemes
from workflows import Workflows

__all__ = [
    "Dashboards",
    "Filters",
    "FilterSharing",
    "Groups",
    "Issues",
    "IssueAttachments",
    "IssueComments",
    "IssueFields",
    "IssueLinks",
    "IssueRemoteLinks",
    "IssueVotes",
    "IssueWatchers",
    "IssueWorklogs",
    "Projects",
    "ProjectCategories",
    "ProjectCategories",
    "ProjectComponents",
    "ProjectRoles",
    "ProjectRoles",
    "ProjectVersions",
    "Screens",
    "Users",
    "Workflows",
    "WorkflowSchemes",
]
