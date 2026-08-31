/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.dataflow

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.config.S3StagingConfiguration
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
internal class RedshiftAggregateFactoryTest {

    @MockK lateinit var redshiftClient: RedshiftAirbyteClient
    @MockK lateinit var streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>

    private val tableName = TableName(namespace = "my_schema", name = "my_table")
    private val storeKey = DestinationStream.Descriptor("my_namespace", "my_stream")

    private val s3Config =
        S3StagingConfiguration(
            s3BucketName = "test-bucket",
            s3BucketRegion = "us-east-1",
            accessKeyId = "AKID",
            secretAccessKey = "SECRET",
        )

    private val configuration =
        RedshiftConfiguration(
            host = "redshift.example.com",
            port = 5439,
            database = "mydb",
            schema = "public",
            username = "admin",
            password = "secret",
            jdbcUrlParams = null,
            uploadingMethod = s3Config,
            tunnelMethod = null,
            dropCascade = false,
        )

    private lateinit var factory: RedshiftAggregateFactory

    @BeforeEach
    fun setUp() {
        factory = RedshiftAggregateFactory(redshiftClient, streamStateStore, configuration)
    }

    @Test
    fun `create resolves table name from stream state store`() {
        val executionConfig = DirectLoadTableExecutionConfig(tableName = tableName)
        every { streamStateStore.get(storeKey) } returns executionConfig
        every { redshiftClient.describeTable(tableName) } returns
            listOf(
                "_airbyte_raw_id",
                "_airbyte_extracted_at",
                "_airbyte_meta",
                "_airbyte_generation_id",
                "col1"
            )

        val aggregate = factory.create(storeKey)

        assertNotNull(aggregate)
        assertTrue(aggregate is RedshiftAggregate)
        verify { streamStateStore.get(storeKey) }
        verify { redshiftClient.describeTable(tableName) }
    }

    @Test
    fun `create calls describeTable with correct table name`() {
        val executionConfig = DirectLoadTableExecutionConfig(tableName = tableName)
        every { streamStateStore.get(storeKey) } returns executionConfig
        every { redshiftClient.describeTable(tableName) } returns listOf("id", "name")

        factory.create(storeKey)

        verify(exactly = 1) { redshiftClient.describeTable(tableName) }
    }

    @Test
    fun `create produces distinct aggregates per invocation`() {
        val executionConfig = DirectLoadTableExecutionConfig(tableName = tableName)
        every { streamStateStore.get(storeKey) } returns executionConfig
        every { redshiftClient.describeTable(tableName) } returns listOf("id")

        val agg1 = factory.create(storeKey)
        val agg2 = factory.create(storeKey)

        // Each invocation should produce a fresh aggregate with its own buffer
        assertTrue(agg1 !== agg2, "Factory should produce distinct aggregate instances")
    }
}
