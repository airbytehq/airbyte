/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.h2.H2TestFixture
import io.airbyte.cdk.h2source.H2SourceConfiguration
import io.airbyte.cdk.h2source.H2SourceOperations
import io.airbyte.cdk.h2source.UserDefinedCursor
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import java.time.Duration
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class SnowflakeSourceMetadataQuerierTest {
    val h2 = H2TestFixture()

    init {
        h2.execute("CREATE SCHEMA TEST_SCHEMA")
        h2.execute("CREATE SCHEMA TESTXSCHEMA")
        h2.execute("CREATE TABLE TEST_SCHEMA.T1 (ID INT, USER_ID INT)")
        h2.execute("CREATE TABLE TESTXSCHEMA.T2 (ID INT, USER_ID INT)")
    }

    fun querier(schema: String?): SnowflakeSourceMetadataQuerier {
        val config =
            H2SourceConfiguration(
                realHost = "localhost",
                realPort = h2.port,
                sshTunnel = SshNoTunnelMethod,
                sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
                jdbcUrlFmt = "jdbc:h2:tcp://%s:%d/mem:${h2.database}",
                namespaces = setOf(h2.database),
                tableFilters = emptyList(),
                cursor = UserDefinedCursor,
                resumablePreferred = true,
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofDays(1),
            )
        val base =
            JdbcMetadataQuerier(
                DefaultJdbcConstants(),
                config,
                H2SourceOperations(),
                H2SourceOperations(),
                JdbcCheckQueries(),
                JdbcConnectionFactory(config),
            )
        return SnowflakeSourceMetadataQuerier(base, schema)
    }

    @Test
    fun schemaFilterMatchesLiterally() {
        val mdq = querier("TEST_SCHEMA")
        Assertions.assertEquals(listOf("TEST_SCHEMA"), mdq.streamNamespaces())
        Assertions.assertEquals(listOf("T1"), mdq.memoizedTableNames.map { it.name })
    }

    @Test
    fun columnsAreNotDuplicated() {
        val mdq = querier("TEST_SCHEMA")
        val table: TableName = mdq.memoizedTableNames.single()
        Assertions.assertEquals("T1", table.name)
        Assertions.assertEquals(
            listOf("ID", "USER_ID"),
            mdq.memoizedColumnMetadata[table]!!.map { it.name },
        )
        mdq.memoizedColumnMetadata.forEach { (t, cols) ->
            Assertions.assertEquals(
                cols.map { it.name }.distinct().size,
                cols.size,
                "duplicate columns discovered for $t",
            )
        }
    }

    @Test
    fun wildcardCharactersInSchemaAreEscaped() {
        val mdq = querier("TEST%")
        Assertions.assertEquals(emptyList<String>(), mdq.streamNamespaces())
        Assertions.assertEquals(emptyList<TableName>(), mdq.memoizedTableNames)
    }
}
