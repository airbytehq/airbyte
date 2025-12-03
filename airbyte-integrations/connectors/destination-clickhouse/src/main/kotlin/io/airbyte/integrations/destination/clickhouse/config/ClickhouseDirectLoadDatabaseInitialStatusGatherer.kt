/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.table.BaseDirectLoadInitialStatusGatherer
import jakarta.inject.Singleton

@Singleton
class ClickhouseDirectLoadDatabaseInitialStatusGatherer(
    tableOperationsClient: TableOperationsClient,
    catalog: DestinationCatalog,
) :
    BaseDirectLoadInitialStatusGatherer(
        tableOperationsClient,
        catalog,
    )
