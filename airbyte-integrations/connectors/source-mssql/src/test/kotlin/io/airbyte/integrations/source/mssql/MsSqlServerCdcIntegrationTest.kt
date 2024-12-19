/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerCdcReplicationConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import java.sql.Connection
import java.sql.Statement

class MsSqlServerCdcIntegrationTest {
       @Test
       fun testBasicCheck() {
           val run1: BufferingOutputConsumer = CliRunner.source("check", config(), null).run()

           assertEquals(run1.messages().size, 1)
           assertEquals(
               run1.messages().first().connectionStatus.status,
               AirbyteConnectionStatus.Status.SUCCEEDED
           )
       }
    @Test
    @Disabled("This should failed because CDC is disabled on the container. The missing code is equivalent to MySqlSourceMetadataQuerier.extraChecks")
    fun testCheckCdcOnNonCdcDb() {
           val nonCdcDbContainer = MsSqlServerContainerFactory.shared(
                   MsSqlServerImage.SQLSERVER_2022
               )
           val invalidConfig: MsSqlServerSourceConfigurationSpecification =
               nonCdcDbContainer.config.apply {
                   replicationMethodJson = MsSqlServerCdcReplicationConfigurationSpecification()
               }

           val run2: BufferingOutputConsumer =
               CliRunner.source("check", invalidConfig, null).run()

           val messageInRun2 =
               run2
                   .messages()
                   .filter { it.type == AirbyteMessage.Type.CONNECTION_STATUS }
                   .first()

           assertEquals(
               AirbyteConnectionStatus.Status.FAILED,
               messageInRun2.connectionStatus.status
           )
       }


       @Test
       fun test() {
           val state1 = CliRunner.source("read", config(), configuredCatalog).run().states().last()

           connectionFactory.get().use { connection: Connection ->
               connection.isReadOnly = false
               connection.createStatement().use { stmt: Statement ->
                   stmt.execute("INSERT INTO test.tbl (k, v) VALUES (3, 'baz')")
               }
           }

           val run2InputState: List<AirbyteStateMessage> = listOf(state1)
           CliRunner.source("read", config(), configuredCatalog, run2InputState).run().records()
       }

       @Test
       fun testFullRefresh() {
           val fullRefreshCatalog =
               configuredCatalog.apply { streams.forEach { it.syncMode = SyncMode.FULL_REFRESH } }
           CliRunner.source("read", config(), fullRefreshCatalog).run()
           connectionFactory.get().use { connection: Connection ->
               connection.isReadOnly = false
               connection.createStatement().use { stmt: Statement ->
                   stmt.execute("INSERT INTO test.tbl (k, v) VALUES (4, 'baz')")
               }
           }
       }

       companion object {
           val log = KotlinLogging.logger {}
           var dbContainer: MsSqlServercontainer = MsSqlServerContainerFactory.exclusive(
               MsSqlServerImage.SQLSERVER_2022,
               MsSqlServerContainerFactory.WithNetwork,
               MsSqlServerContainerFactory.WithCdcAgent
           )

           fun config(): MsSqlServerSourceConfigurationSpecification =
               dbContainer.config.apply {
                   replicationMethodJson = MsSqlServerCdcReplicationConfigurationSpecification()
               }

           val connectionFactory: JdbcConnectionFactory by lazy {
               JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config()))
           }

           val configuredCatalog: ConfiguredAirbyteCatalog = run {
               val desc = StreamDescriptor().withName("id_name_and_born").withNamespace(dbContainer.schemaName)
               val discoveredStream =
                   DiscoveredStream(
                       id = StreamIdentifier.Companion.from(desc),
                       columns = listOf(Field("k", IntFieldType), Field("v", StringFieldType)),
                       primaryKeyColumnIDs = listOf(listOf("k")),
                   )
               val stream: AirbyteStream = MsSqlServerStreamFactory().createGlobal(discoveredStream)
               val configuredStream: ConfiguredAirbyteStream =
                   CatalogHelpers.toDefaultConfiguredStream(stream)
                       .withSyncMode(SyncMode.INCREMENTAL)
                       .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                       .withCursorField(listOf(MsSqlServerStreamFactory.MsSqlServerCdcMetaFields.CDC_CURSOR.id))
               ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
           }

       }


}
