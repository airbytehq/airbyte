/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

class MysqlCdcIntegrationTest {
    /*
       @Test
       fun testCheck() {
           val run1: BufferingOutputConsumer = CliRunner.source("check", config(), null).run()

           assertEquals(run1.messages().size, 1)
           assertEquals(
               run1.messages().first().connectionStatus.status,
               AirbyteConnectionStatus.Status.SUCCEEDED
           )

           MsSqlServerContainerFactory.exclusive(
                   imageName = "mysql:8.0",
               MsSqlServerContainerFactory.WithCdcOff,
               )
               .use { nonCdcDbContainer ->
                   {
                       val invalidConfig: MsSqlServerSourceConfigurationSpecification =
                           MsSqlServerContainerFactory.config(nonCdcDbContainer).apply {
                               setMethodValue(CdcCursor())
                           }

                       val nonCdcConnectionFactory =
                           JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(invalidConfig))

                       provisionTestContainer(nonCdcDbContainer, nonCdcConnectionFactory)

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
               }
       }

       @Test
       fun test() {
           CliRunner.source("read", config(), configuredCatalog).run()
           // TODO: add assertions on run1 messages.

           connectionFactory.get().use { connection: Connection ->
               connection.isReadOnly = false
               connection.createStatement().use { stmt: Statement ->
                   stmt.execute("INSERT INTO test.tbl (k, v) VALUES (3, 'baz')")
               }
           }
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
           lateinit var dbContainer: MSSQLServerContainer<*>

           fun config(): MsSqlServerSourceConfigurationSpecification =
               MsSqlServerContainerFactory.config(dbContainer).apply { setMethodValue(CdcCursor()) }

           val connectionFactory: JdbcConnectionFactory by lazy {
               JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config()))
           }

           val configuredCatalog: ConfiguredAirbyteCatalog = run {
               val desc = StreamDescriptor().withName("tbl").withNamespace("test")
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
                       .withCursorField(listOf(MysqlCdcMetaFields.CDC_CURSOR.id))
               ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
           }

           @JvmStatic
           @BeforeAll
           @Timeout(value = 300)
           fun startAndProvisionTestContainer() {
               dbContainer =
                   MsSqlServerContainerFactory.exclusive(
                       imageName = "mysql:8.0",
                       MsSqlServerContainerFactory.WithNetwork,
                   )
               provisionTestContainer(dbContainer, connectionFactory)
           }

           fun provisionTestContainer(
               targetContainer: MSSQLServerContainer<*>,
               targetConnectionFactory: JdbcConnectionFactory
           ) {
               val gtidOn =
                   "SET @@GLOBAL.ENFORCE_GTID_CONSISTENCY = 'ON';" +
                       "SET @@GLOBAL.GTID_MODE = 'OFF_PERMISSIVE';" +
                       "SET @@GLOBAL.GTID_MODE = 'ON_PERMISSIVE';" +
                       "SET @@GLOBAL.GTID_MODE = 'ON';"
               val grant =
                   "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT " +
                       "ON *.* TO '${targetContainer.username}'@'%';"
               targetContainer.execAsRoot(gtidOn)
               targetContainer.execAsRoot(grant)
               targetContainer.execAsRoot("FLUSH PRIVILEGES;")

               targetConnectionFactory.get().use { connection: Connection ->
                   connection.isReadOnly = false
                   connection.createStatement().use { stmt: Statement ->
                       stmt.execute("CREATE TABLE test.tbl(k INT PRIMARY KEY, v VARCHAR(80))")
                   }
                   connection.createStatement().use { stmt: Statement ->
                       stmt.execute("INSERT INTO test.tbl (k, v) VALUES (1, 'foo'), (2, 'bar')")
                   }
               }
           }
       }

    */
}
