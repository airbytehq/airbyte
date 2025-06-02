package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.BaseDatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

class ClickhouseDirectLoadDatabaseInitialStatusGatherer(
    airbyteClient: AirbyteClient,
    clickhouseConfiguration: ClickhouseConfiguration,
    internalTableDataset: String = "airbyte_internal",
) : BaseDatabaseInitialStatusGatherer<DirectLoadInitialStatus>(
    airbyteClient,
    clickhouseConfiguration.resolvedDatabase,
    internalTableDataset,
)
