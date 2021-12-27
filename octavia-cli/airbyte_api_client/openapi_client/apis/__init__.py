#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.connection_api import ConnectionApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from openapi_client.api.connection_api import ConnectionApi
from openapi_client.api.db_migration_api import DbMigrationApi
from openapi_client.api.deployment_api import DeploymentApi
from openapi_client.api.destination_api import DestinationApi
from openapi_client.api.destination_definition_api import DestinationDefinitionApi
from openapi_client.api.destination_definition_specification_api import DestinationDefinitionSpecificationApi
from openapi_client.api.health_api import HealthApi
from openapi_client.api.jobs_api import JobsApi
from openapi_client.api.logs_api import LogsApi
from openapi_client.api.notifications_api import NotificationsApi
from openapi_client.api.oauth_api import OauthApi
from openapi_client.api.openapi_api import OpenapiApi
from openapi_client.api.operation_api import OperationApi
from openapi_client.api.scheduler_api import SchedulerApi
from openapi_client.api.source_api import SourceApi
from openapi_client.api.source_definition_api import SourceDefinitionApi
from openapi_client.api.source_definition_specification_api import SourceDefinitionSpecificationApi
from openapi_client.api.web_backend_api import WebBackendApi
from openapi_client.api.workspace_api import WorkspaceApi
