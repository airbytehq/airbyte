/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.integration

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.registerKotlinModule
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlSpecification
import io.airbyte.integrations.destination.mysql_v2.spec.SslMode
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MySQLContainer
import org.testcontainers.utility.DockerImageName

private val log = KotlinLogging.logger {}

class MysqlBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        configContents = createTestcontainersConfig(),
        configSpecClass = MysqlSpecification::class.java,
        dataDumper = MysqlTestDataDumper,
        destinationCleaner = MysqlTestDestinationCleaner,
        recordMangler = NoopExpectedRecordMapper,
        verifyDataWriting = true,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(
            cdcDeletionMode = DedupBehavior.CdcDeletionMode.HARD_DELETE
        ),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        supportFileTransfer = false,
        commitDataIncrementally = true,
        allTypesBehavior = StronglyTyped(
            convertAllValuesToString = false,
            topLevelFloatLosesPrecision = false,
            nestedFloatLosesPrecision = false,
            integerCanBeLarge = true,
            numberCanBeLarge = true,
            numberIsFixedPointPrecision38Scale9 = true,
            truncatedNumbersPopulateAirbyteMeta = true,
        ),
    ) {

    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    override fun testMidSyncCheckpointingStreamState() {
        super.testMidSyncCheckpointingStreamState()
    }

    @Test
    override fun testNamespaces() {
        super.testNamespaces()
    }

    @Test
    override fun testAppend() {
        super.testAppend()
    }

    @Test
    override fun testTruncateRefresh() {
        super.testTruncateRefresh()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Test
    override fun testDedup() {
        super.testDedup()
    }

    companion object {
        private val container: MySQLContainer<*> by lazy {
            MySQLContainer(DockerImageName.parse("mysql:8.0"))
                .withDatabaseName("test_db")
                .withUsername("root")
                .withPassword("test_password")
                .withCommand(
                    "--character-set-server=utf8mb4",
                    "--collation-server=utf8mb4_unicode_ci",
                    "--max_allowed_packet=67108864", // 64MB for large batches
                    "--sql-mode=NO_ENGINE_SUBSTITUTION" // Relaxed SQL mode for temp table TIMESTAMP defaults
                )
                .apply { start() }
        }

        private fun createTestcontainersConfig(): String {
            val mapper = ObjectMapper().registerKotlinModule()
            val config = mapOf(
                "host" to container.host,
                "port" to container.firstMappedPort,
                "database" to container.databaseName,
                "username" to "root",
                "password" to container.password,
                "ssl" to false,
                "ssl_mode" to "DISABLED",
                "jdbc_url_params" to null,
                "batch_size" to 5000
            )
            return mapper.writeValueAsString(config)
        }
    }
}
