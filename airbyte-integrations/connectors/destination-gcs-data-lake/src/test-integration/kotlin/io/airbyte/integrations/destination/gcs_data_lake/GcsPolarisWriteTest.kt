package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.write.*
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeSpecification
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@Execution(ExecutionMode.SAME_THREAD)
class GcsPolarisWriteTest :
    BasicFunctionalityIntegrationTest(
        configContents = getConfig(),
        configSpecClass = GcsDataLakeSpecification::class.java,
        dataDumper =
            BigLakeDataDumper(
                delegateDataDumper =
                    io.airbyte.cdk.load.data.icerberg.parquet.IcebergDataDumper(
                        tableIdGenerator = SimpleTableIdGenerator(),
                        getCatalog = { spec ->
                            GcsDataLakeTestUtil.getCatalog(GcsDataLakeTestUtil.getConfig(spec))
                        }
                    )
            ),
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = io.airbyte.cdk.load.data.icerberg.parquet.IcebergExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.SOFT_DELETE),
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
        configUpdater = io.airbyte.cdk.load.data.icerberg.parquet.IcebergConfigUpdater,
        useDataFlowPipeline = true
    ) {

    @Test
    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/11439")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    companion object {
        fun getConfig(): String = PolarisEnvironment.getConfig()

        @JvmStatic
        @BeforeAll
        fun setup() {
            PolarisEnvironment.startServices()
        }

        @JvmStatic
        @AfterAll
        fun stop() {
            PolarisEnvironment.stopServices()
        }
    }
}
