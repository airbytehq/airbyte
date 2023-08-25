#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_google_workspace_admin_reports import SourceGoogleWorkspaceAdminReports

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGoogleWorkspaceAdminReports()
    launch(source, sys.argv[1:])
