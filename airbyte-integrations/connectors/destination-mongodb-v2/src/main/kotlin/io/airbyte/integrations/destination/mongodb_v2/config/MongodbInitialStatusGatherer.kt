/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.config

import io.airbyte.cdk.load.orchestration.db.BaseDirectLoadInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.integrations.destination.mongodb_v2.client.MongodbAirbyteClient
import jakarta.inject.Singleton

@Singleton
class MongodbInitialStatusGatherer(
    mongodbClient: MongodbAirbyteClient,
    tempTableNameGenerator: TempTableNameGenerator,
) :
    BaseDirectLoadInitialStatusGatherer(mongodbClient, tempTableNameGenerator),
    DatabaseInitialStatusGatherer<DirectLoadInitialStatus>
