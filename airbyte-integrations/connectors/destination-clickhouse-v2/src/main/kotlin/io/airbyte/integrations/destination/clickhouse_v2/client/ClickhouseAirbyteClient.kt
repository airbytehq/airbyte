package io.airbyte.integrations.destination.clickhouse_v2.client

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.clickhouse.data.ClickHouseDataType
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

val log = KotlinLogging.logger {  }

@Singleton
class ClickhouseAirbyteClient(private val client: Client
    ): AirbyteClient<ClickHouseDataType>() {
    override fun getNumberOfRecordsInTable(tableName: TableName): Long? {
        try {
            val response = client.query("SELECT count(1) cnt FROM `${tableName.namespace}`.`${tableName.name}`;").get()
            val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
            reader.next()
            val count = reader.getLong("cnt")
            return count
        } catch (e: Exception) {
            return null
        }
    }

    override fun getGenerationId(tableName: TableName): Long {
        try {
            val generationAlias = "generation"
            val response = client.query("SELECT _airbyte_generation_id $generationAlias FROM `${tableName.namespace}`.`${tableName.name}` LIMIT 1;").get()
            val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
            reader.next()
            val generation = reader.getLong(generationAlias)
            return generation
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve the generation Id" }
            // TODO: open question: Do we need to raise an error here or just return 0?
            return 0;
        }
    }

    /**
     * Executes a query against the ClickHouse database. The response of the query is not returned.
     *
     * @param query The SQL query to execute.
     * @return A boolean indicating whether the query was executed successfully.
     */
    override fun executeQuery(query: String): Boolean {
        try {
            client.execute(query).get()
            return true
        } catch (e: Exception) {
            log.error(e) { "Fail to run query." }
            return false
        }
    }

    override fun getCreateTableSuffix(): String {
        return """
            ENGINE = MergeTree()
            ORDER BY ();
        """.trimIndent()
    }

    override fun toDialectType(type: AirbyteType): ClickHouseDataType =
        when (type) {
            BooleanType -> ClickHouseDataType.Bool
            DateType -> ClickHouseDataType.Date
            IntegerType -> ClickHouseDataType.Int64
            NumberType -> ClickHouseDataType.Int256
            StringType -> ClickHouseDataType.String
            TimeTypeWithTimezone -> ClickHouseDataType.String
            TimeTypeWithoutTimezone -> ClickHouseDataType.DateTime
            TimestampTypeWithTimezone -> ClickHouseDataType.DateTime
            TimestampTypeWithoutTimezone -> ClickHouseDataType.DateTime
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema -> ClickHouseDataType.JSON
            is UnionType ->
                if (type.isLegacyUnion) {
                    ClickhouseDirectLoadSqlGenerator.toDialectType(type.chooseType())
                } else {
                    ClickHouseDataType.JSON
                }
            is UnknownType -> ClickHouseDataType.JSON
        }
}
