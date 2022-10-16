#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_workspace_admin_reports import SourceGoogleWorkspaceAdminReports

if __name__ == "__main__":
    source = SourceGoogleWorkspaceAdminReports()
    launch(source, sys.argv[1:])
