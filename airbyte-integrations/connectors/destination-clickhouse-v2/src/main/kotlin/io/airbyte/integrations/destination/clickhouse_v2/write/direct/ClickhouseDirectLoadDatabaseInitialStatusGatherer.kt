/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.orchestration.db.BaseDirectLoadInitialStatusGatherer
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
class ClickhouseDirectLoadDatabaseInitialStatusGatherer(
    airbyteClient: AirbyteClient,
    @Named("internalNamespace") internalNamespace: String,
) :
    BaseDirectLoadInitialStatusGatherer(
        airbyteClient,
        internalNamespace,
    )
