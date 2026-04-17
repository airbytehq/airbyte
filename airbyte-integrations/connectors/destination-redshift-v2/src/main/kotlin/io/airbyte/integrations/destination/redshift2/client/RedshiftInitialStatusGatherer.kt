/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.client

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.table.BaseDirectLoadInitialStatusGatherer
import jakarta.inject.Singleton

/**
 * Gathers initial table status for all streams in the catalog.
 *
 * Delegates entirely to the CDK's [BaseDirectLoadInitialStatusGatherer], which uses
 * [TableOperationsClient.countTable] to determine whether each stream's final and temp tables exist
 * and whether they are empty.
 */
@Singleton
class RedshiftInitialStatusGatherer(
    tableOperationsClient: TableOperationsClient,
    catalog: DestinationCatalog,
) : BaseDirectLoadInitialStatusGatherer(tableOperationsClient, catalog)
