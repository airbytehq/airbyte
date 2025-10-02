package io.airbyte.integrations.destination.motherduck.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckConfiguration
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckConfigurationFactory
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckSpecification
import java.nio.file.Path
import java.nio.file.Paths

internal val CONFIG_PATH: Path = Paths.get("secrets/config.json")

class MotherDuckAcceptanceTest :
    BasicFunctionalityIntegrationTest(
        configContents = "{}",
        configSpecClass = MotherDuckSpecification::class.java,
        dataDumper = MotherDuckDataDumper { spec ->
            MotherDuckConfigurationFactory().make(spec as MotherDuckSpecification)
        },
        destinationCleaner = MotherDuckDataCleaner,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = true,
                numberCanBeLarge = true,
                nestedFloatLosesPrecision = false,
            ),
        recordMangler = MotherDuckExpectedRecordMapper,
    )

class MotherDuckDataDumper(
    private val configProvider: (ConfigurationSpecification) -> MotherDuckConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        return emptyList()
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("MotherDuck does not support file transfer.")
    }
}

object MotherDuckDataCleaner : DestinationCleaner {
    override fun cleanup() {
    }
}

object MotherDuckExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord = expectedRecord
}
