/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.redshift.config.RedshiftSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

/**
 * Full end-to-end acceptance test for the Redshift destination in S3 staging mode.
 *
 * Runs the connector as a process via the CDK test harness and verifies typed final-table output.
 * Config is read from the `secrets/test_cluster.json` secrets file, which must contain valid
 * Redshift cluster + S3 staging credentials.
 */
abstract class RedshiftBaseAcceptanceTest(
    dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
    dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    unknownTypesBehavior: UnknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    isStreamSchemaRetroactiveForUnknownTypeToString: Boolean = true,
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Path.of(CONFIG_PATH)),
        configSpecClass = RedshiftSpecification::class.java,
        dataDumper = RedshiftDataDumper { RedshiftTestConfigProvider.configFrom(it) },
        destinationCleaner = RedshiftDataCleaner,
        recordMangler = RedshiftExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        isStreamSchemaRetroactiveForUnknownTypeToString =
            isStreamSchemaRetroactiveForUnknownTypeToString,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.STRINGIFY,
        stringifyUnionObjects = true,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
                numberIsFixedPointPrecision38Scale9 = true,
                truncatedNumbersPopulateAirbyteMeta = false,
            ),
        unknownTypesBehavior = unknownTypesBehavior,
        nullEqualsUnset = true,
        dataChannelFormat = dataChannelFormat,
        dataChannelMedium = dataChannelMedium,
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun warmUpSharedDataSource() {
            RedshiftTestDataSourceProvider.get()
        }

        @JvmStatic
        @AfterAll
        fun closeSharedDataSource() {
            RedshiftTestDataSourceProvider.close()
        }
    }
}

/** Default acceptance test using JSONL over STDIO (standard data channel). */
class RedshiftAcceptanceTest : RedshiftBaseAcceptanceTest() {
    @Test
    @Disabled("Disabled due to frequent timeouts syncing 21 streams via S3 staging")
    override fun testManyStreamsCompletion() {
        super.testManyStreamsCompletion()
    }

    @Test
    @Disabled("Disabled due to frequent timeouts syncing 13 funky-character streams via S3 staging")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }
}

/**
 * Acceptance test using Protobuf over Socket data channel. Protobuf cannot represent unknown types,
 * so those are nullified instead of passed through.
 */
class RedshiftProtoAcceptanceTest :
    RedshiftBaseAcceptanceTest(
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
    )
