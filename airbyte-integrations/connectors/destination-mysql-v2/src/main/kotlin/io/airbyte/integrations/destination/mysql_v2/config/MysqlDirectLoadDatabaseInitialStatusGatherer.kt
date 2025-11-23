/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.config

import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.orchestration.db.BaseDirectLoadInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import jakarta.inject.Singleton

/**
 * MySQL implementation of initial status gatherer for direct load.
 * Extends the base implementation without requiring custom logic.
 */
@Singleton
class MysqlDirectLoadDatabaseInitialStatusGatherer(
    tableOperationsClient: TableOperationsClient,
    tempTableNameGenerator: TempTableNameGenerator,
) :
    BaseDirectLoadInitialStatusGatherer(
        tableOperationsClient,
        tempTableNameGenerator,
    )
