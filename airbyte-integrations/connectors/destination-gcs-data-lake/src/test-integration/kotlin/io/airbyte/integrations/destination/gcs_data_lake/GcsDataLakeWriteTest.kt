/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.icerberg.parquet.IcebergConfigUpdater
import io.airbyte.cdk.load.data.icerberg.parquet.IcebergDataDumper
import io.airbyte.cdk.load.data.icerberg.parquet.IcebergExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.write.*
import io.airbyte.integrations.destination.gcs_data_lake.catalog.BigLakeTableIdGenerator
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeSpecification
import java.nio.file.Files
import kotlin.test.assertContains
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

/**
 * BigLake write test with column name mapping.
 *
 * Column names are sanitized (alphanumeric + underscore) in the Iceberg schema for BigLake
 * compatibility. The BigLakeDataDumper reverse-maps column names when reading data for test
 * validation.
 */
class BigLakeWriteTest :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(GcsDataLakeTestUtil.BIGLAKE_CONFIG_PATH),
        configSpecClass = GcsDataLakeSpecification::class.java,
        dataDumper =
            BigLakeDataDumper(
                delegateDataDumper =
                    IcebergDataDumper(
                        tableIdGenerator = BigLakeTableIdGenerator("test_database"),
                        getCatalog = { spec ->
                            GcsDataLakeTestUtil.getCatalog(GcsDataLakeTestUtil.getConfig(spec))
                        }
                    )
            ),
        destinationCleaner = NoopDestinationCleaner, // TODO: Implement proper cleaner
        recordMangler = IcebergExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
        dedupBehavior = DedupBehavior(),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.STRINGIFY,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior =
            StronglyTyped(integerCanBeLarge = false, nestedFloatLosesPrecision = false),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        configUpdater = IcebergConfigUpdater,
    ) {

    @Test
    override fun testUnions() {
        super.testUnions()
    }

    @Test
    override fun testBasicTypes() {
        super.testBasicTypes()
    }

    @Test
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

//    @Disabled
    @Test
    override fun testDedup() {
        super.testDedup()
    }

    @Test
    fun testNameConflicts() {
        assumeTrue(verifyDataWriting)
        fun makeStream(
            name: String,
            namespaceSuffix: String,
        ) =
            DestinationStream(
                unmappedNamespace = randomizedNamespace + namespaceSuffix,
                unmappedName = name,
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper()
            )
        // Glue downcases stream IDs, and also coerces to alphanumeric+underscore.
        // So these two streams will collide.
        val catalog =
            DestinationCatalog(
                listOf(
                    makeStream("stream_with_spécial_character+", "_FOO"),
                    makeStream("stream_with_spécial_character$", "_FOO"),
                )
            )

        val failure = expectFailure { runSync(updatedConfig, catalog, messages = emptyList()) }
        assertContains(failure.message, "Detected naming conflicts between streams")
    }

    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }
}
