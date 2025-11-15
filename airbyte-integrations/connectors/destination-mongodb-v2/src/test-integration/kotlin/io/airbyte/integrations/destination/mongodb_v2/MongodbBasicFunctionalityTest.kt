/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.mongodb_v2.config.MongodbSpecification
import java.nio.file.Path
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class MongodbBasicFunctionalityTest : BasicFunctionalityIntegrationTest(
    configContents = Path.of("secrets/config.json").toFile().readText(),
    configSpecClass = MongodbSpecification::class.java,
    dataDumper = createDataDumper(),
    destinationCleaner = createCleaner(),
    recordMangler = NoopExpectedRecordMapper,
    nameMapper = NoopNameMapper,
    configUpdater = MongodbConfigUpdater(),

    // Schema behavior - MongoDB is schemaless, changes are NOT retroactive
    isStreamSchemaRetroactive = false,

    // CDC/Dedupe behavior - MongoDB supports soft delete (keeps deletion metadata)
    dedupBehavior = io.airbyte.cdk.load.write.DedupBehavior(io.airbyte.cdk.load.write.DedupBehavior.CdcDeletionMode.SOFT_DELETE),

    // Type handling - MongoDB stores everything so use PASS_THROUGH
    stringifySchemalessObjects = false,
    schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
    schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
    unionBehavior = UnionBehavior.PASS_THROUGH,

    // Feature support
    supportFileTransfer = false,  // Database destination
    commitDataIncrementally = true,  // MongoDB commits immediately
    useDataFlowPipeline = true,  // Use the dataflow pipeline (WriteOperationV2)

    // Type system behavior
    allTypesBehavior = StronglyTyped(
        integerCanBeLarge = true,   // MongoDB Int64 supports large integers
        numberCanBeLarge = true,    // MongoDB Double has good precision
        nestedFloatLosesPrecision = false,
    ),
    unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    nullEqualsUnset = true,
) {
    companion object {
        private lateinit var testMongoClient: com.mongodb.kotlin.client.coroutine.MongoClient
        private lateinit var dataDumperInstance: MongodbDataDumper
        private lateinit var cleanerInstance: MongodbCleaner

        @JvmStatic
        @BeforeAll
        fun setup() {
            // Get MongoClient from Testcontainers
            testMongoClient = createTestMongoClient()
            // Create singleton instances
            dataDumperInstance = MongodbDataDumper(testMongoClient, "test")
            cleanerInstance = MongodbCleaner(testMongoClient, "test")
        }

        @JvmStatic
        fun createDataDumper(): MongodbDataDumper {
            return dataDumperInstance
        }

        @JvmStatic
        fun createCleaner(): MongodbCleaner {
            return cleanerInstance
        }

        private fun createTestMongoClient(): com.mongodb.kotlin.client.coroutine.MongoClient {
            // Use the same Testcontainers instance
            val connectionString = MongodbContainerHelper.getConnectionString()
            val settings = com.mongodb.MongoClientSettings.builder()
                .applyConnectionString(com.mongodb.ConnectionString(connectionString))
                .build()
            return com.mongodb.kotlin.client.coroutine.MongoClient.create(settings)
        }
    }

    // Enable tests as features are implemented

    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
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
    override fun testDedup() {
        super.testDedup()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }
}
