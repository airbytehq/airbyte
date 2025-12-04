/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.table.BaseDirectLoadInitialStatusGatherer
import jakarta.inject.Singleton

@Singleton
class PostgresDirectLoadDatabaseInitialStatusGatherer(
    airbyteClient: TableOperationsClient,
    catalog: DestinationCatalog,
) :
    BaseDirectLoadInitialStatusGatherer(
        airbyteClient,
        catalog,
    )
