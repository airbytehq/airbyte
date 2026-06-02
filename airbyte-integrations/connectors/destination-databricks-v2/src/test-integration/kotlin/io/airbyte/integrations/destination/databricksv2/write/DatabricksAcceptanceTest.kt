/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Specification
import java.nio.file.Files
import java.nio.file.Path

/**
 * Full end-to-end acceptance test for the Databricks v2 destination. Runs the connector as a
 * process via the CDK test harness and verifies typed final-table output.
 *
 * Config is read from the `secrets/config.json` secrets file, which must contain valid Databricks
 * cluster credentials (hostname, http_path, database, authentication).
 */
abstract class DatabricksBaseAcceptanceTest(
    dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
    dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    unknownTypesBehavior: UnknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Path.of(CONFIG_PATH)),
        configSpecClass = DatabricksV2Specification::class.java,
        dataDumper = DatabricksDataDumper { DatabricksTestConfigProvider.configFrom(it) },
        destinationCleaner = DatabricksDataCleaner,
        recordMangler = DatabricksExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.STRINGIFY,
        commitDataIncrementally = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
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
    )
