/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.client

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.table.BaseDirectLoadInitialStatusGatherer
import jakarta.inject.Singleton

/** Gathers the initial real/temp table status for each configured Firebolt stream. */
@Singleton
class FireboltInitialStatusGatherer(
    tableOperationsClient: TableOperationsClient,
    catalog: DestinationCatalog,
) : BaseDirectLoadInitialStatusGatherer(tableOperationsClient, catalog)
