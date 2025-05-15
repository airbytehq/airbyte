/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.check

import io.airbyte.cdk.load.check.CheckCleaner
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.bigquery.BigqueryBeansFactory
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryFinalTableNameGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryRawTableNameGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.toTableId

class BigqueryCheckCleaner : CheckCleaner<BigqueryConfiguration> {
    override fun cleanup(config: BigqueryConfiguration, stream: DestinationStream) {
        val bq = BigqueryBeansFactory().getBigqueryClient(config)
        bq.getTable(
                BigqueryRawTableNameGenerator(config).getTableName(stream.descriptor).toTableId()
            )
            ?.delete()
        bq.getTable(
                BigqueryFinalTableNameGenerator(config).getTableName(stream.descriptor).toTableId()
            )
            ?.delete()
    }
}
