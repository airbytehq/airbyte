/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.json.Jsons.clone
import java.util.stream.Collectors
import org.jooq.DSLContext
import org.jooq.Record
import org.mockito.Mockito.mock

abstract class AbstractPostgresDestinationAcceptanceTest : JdbcDestinationAcceptanceTest() {
    private val namingResolver = StandardNameTransformer()
    protected var testDb: PostgresTestDatabase = mock()

    @Throws(Exception::class)
    override fun getFailCheckConfig(): JsonNode? {
        val clone = clone(getConfig())
        (clone as ObjectNode).put("password", "wrong password")
        return clone
    }

    @Throws(Exception::class)
    override fun retrieveNormalizedRecords(
        testEnv: TestDestinationEnv?,
        streamName: String?,
        namespace: String?
    ): List<JsonNode> {
        val tableName = namingResolver.getIdentifier(streamName!!)
        return retrieveRecordsFromTable(tableName, namespace)
    }

    // namingResolver.getRawTableName is deprecated
    @Suppress("deprecation")
    @Throws(Exception::class)
    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
            .stream()
            .map { r: JsonNode -> r[JavaBaseConstants.COLUMN_NAME_DATA] }
            .collect(Collectors.toList())
    }

    @Throws(Exception::class)
    protected open fun retrieveRecordsFromTable(
        tableName: String?,
        schemaName: String?
    ): List<JsonNode> {
        // TODO: Change emitted_at with DV2
        return testDb.query { ctx: DSLContext ->
            ctx.execute("set time zone 'UTC';")
            ctx.fetch(
                    String.format(
                        "SELECT * FROM %s.%s ORDER BY %s ASC;",
                        schemaName,
                        tableName,
                        JavaBaseConstants.COLUMN_NAME_EMITTED_AT
                    )
                )
                .stream()
                .map { record: Record? -> this.getJsonFromRecord(record!!) }
                .collect(Collectors.toList())
        }!!
    }

    override fun implementsNamespaces(): Boolean {
        return true
    }

    override fun getTestDataComparator(): TestDataComparator {
        return PostgresTestDataComparator()
    }

    override fun supportBasicDataTypeTest(): Boolean {
        return true
    }

    override fun supportArrayDataTypeTest(): Boolean {
        return true
    }

    override fun supportObjectDataTypeTest(): Boolean {
        return true
    }

    override fun supportsInDestinationNormalization(): Boolean {
        return true
    }

    override val imageName: String = "airbyte/destination-postgres:dev"
}
