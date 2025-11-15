package io.airbyte.integrations.destination.mysql.config

import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.orchestration.db.BaseDirectLoadInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import jakarta.inject.Singleton

@Singleton
class MySQLDirectLoadDatabaseInitialStatusGatherer(
    tableOperationsClient: TableOperationsClient,
    tempTableNameGenerator: TempTableNameGenerator,
) : BaseDirectLoadInitialStatusGatherer(
    tableOperationsClient,
    tempTableNameGenerator,
)
