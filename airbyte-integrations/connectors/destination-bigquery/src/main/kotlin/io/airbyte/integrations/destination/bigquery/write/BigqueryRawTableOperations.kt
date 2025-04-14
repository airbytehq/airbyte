package io.airbyte.integrations.destination.bigquery.write

import io.airbyte.cdk.load.orchestration.TableName
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingRawTableOperations

class BigqueryRawTableOperations : TypingDedupingRawTableOperations {
    override fun prepareRawTable(rawTableName: TableName, suffix: String, replace: Boolean) {
        TODO("Not yet implemented")
    }

    override fun overwriteRawTable(rawTableName: TableName, suffix: String) {
        TODO("Not yet implemented")
    }

    override fun transferFromTempRawTable(rawTableName: TableName, suffix: String) {
        TODO("Not yet implemented")
    }

    override fun getRawTableGeneration(rawTableName: TableName, suffix: String): Long? {
        TODO("Not yet implemented")
    }

    override fun cleanupStage(rawTableName: TableName) {
        TODO("Not yet implemented")
    }
}
