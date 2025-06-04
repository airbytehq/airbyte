package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseDatabaseHandler

class ClickhouseDirectLoadSqlTableOperations(
    sqlGenerator: ClickhouseDirectLoadSqlGenerator,
    destinationHandler: ClickhouseDatabaseHandler,
) : DefaultDirectLoadTableSqlOperations(sqlGenerator, destinationHandler)
