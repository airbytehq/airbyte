/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.table.BaseDirectLoadInitialStatusGatherer
import jakarta.inject.Singleton

@Singleton
class DatabricksInitialStatusGatherer(
    tableOperationsClient: TableOperationsClient,
    catalog: DestinationCatalog,
) : BaseDirectLoadInitialStatusGatherer(tableOperationsClient, catalog)
