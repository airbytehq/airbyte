/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.config

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.orchestration.db.BaseDirectLoadInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import jakarta.inject.Singleton

@Singleton
class SnowflakeDirectLoadDatabaseInitialStatusGatherer(
    airbyteClient: AirbyteClient,
    tempTableNameGenerator: TempTableNameGenerator,
) :
    BaseDirectLoadInitialStatusGatherer(
        airbyteClient,
        tempTableNameGenerator,
    )
