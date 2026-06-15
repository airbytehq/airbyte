/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.databricksv2.spec.CdcDeletionMode
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Specification
import java.nio.file.Files
import java.nio.file.Path

/**
 * Full end-to-end acceptance test for the Databricks v2 destination. Runs the connector as a
 * process via the CDK test harness and verifies typed final-table output.
 */
abstract class DatabricksBaseAcceptanceTest(
    dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
    dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    unknownTypesBehavior: UnknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    isStreamSchemaRetroactiveForUnknownTypeToString: Boolean = true,
    cdcDeletionMode: CdcDeletionMode = CdcDeletionMode.HARD_DELETE,
) :
    BasicFunctionalityIntegrationTest(
        configContents = createConfigWithCdcMode(cdcDeletionMode),
        configSpecClass = DatabricksV2Specification::class.java,
        dataDumper = DatabricksDataDumper { DatabricksTestConfigProvider.configFrom(it) },
        destinationCleaner = DatabricksDataCleaner,
        recordMangler = DatabricksExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        isStreamSchemaRetroactiveForUnknownTypeToString =
            isStreamSchemaRetroactiveForUnknownTypeToString,
        dedupBehavior =
            DedupBehavior(
                when (cdcDeletionMode) {
                    CdcDeletionMode.HARD_DELETE -> DedupBehavior.CdcDeletionMode.HARD_DELETE
                    CdcDeletionMode.SOFT_DELETE -> DedupBehavior.CdcDeletionMode.SOFT_DELETE
                }
            ),
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
                nestedFloatLosesPrecision = false,
            ),
        unknownTypesBehavior = unknownTypesBehavior,
        nullEqualsUnset = true,
        dataChannelFormat = dataChannelFormat,
        dataChannelMedium = dataChannelMedium,
    )

/** Default acceptance test using JSONL over STDIO (standard data channel). */
class DatabricksAcceptanceTest : DatabricksBaseAcceptanceTest()

/**
 * Acceptance test using Protobuf over Socket data channel. Protobuf cannot represent unknown types,
 * so those are nullified instead of passed through.
 */
class DatabricksProtoAcceptanceTest :
    DatabricksBaseAcceptanceTest(
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
    )

class DatabricksSoftDeleteAcceptanceTest :
    DatabricksBaseAcceptanceTest(cdcDeletionMode = CdcDeletionMode.SOFT_DELETE)

/** Reads the base config JSON and injects the `cdc_deletion_mode` property */
private fun createConfigWithCdcMode(cdcDeletionMode: CdcDeletionMode): String {
    val configStr = Files.readString(Path.of(CONFIG_PATH))
    if (cdcDeletionMode == CdcDeletionMode.HARD_DELETE) {
        return configStr
    }
    val config = Jsons.readTree(configStr) as ObjectNode
    config.put("cdc_deletion_mode", cdcDeletionMode.cdcDeletionMode)
    return Jsons.writeValueAsString(config)
}
