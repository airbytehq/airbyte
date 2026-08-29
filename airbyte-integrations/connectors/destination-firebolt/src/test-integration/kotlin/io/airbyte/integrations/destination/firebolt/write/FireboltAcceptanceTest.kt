/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.write

import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.ColumnDropBehavior
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.firebolt.config.FireboltSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Disabled

/**
 * Airbyte V2 basic-functionality acceptance test for the Firebolt destination.
 *
 * This follows the standard CDK destination acceptance test pattern. It is disabled by default
 * because it requires a real Firebolt cluster plus S3 staging credentials in
 * `src/test-integration/resources/secrets/test_cluster.json`.
 */
const val CONFIG_PATH = "src/test-integration/resources/secrets/test_cluster.json"

@Disabled("Requires a real Firebolt cluster and S3 staging credentials in $CONFIG_PATH")
class FireboltAcceptanceTest :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Path.of(CONFIG_PATH)),
        configSpecClass = FireboltSpecification::class.java,
        dataDumper = FakeDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = NoopExpectedRecordMapper,
        nameMapper = NoopNameMapper,
        isStreamSchemaRetroactive = true,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
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
                numberCanBeLarge = true,
                numberIsFixedPointPrecision38Scale9 = false,
                truncatedNumbersPopulateAirbyteMeta = false,
            ),
        columnDropBehavior = ColumnDropBehavior.RETAIN,
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        dataChannelFormat = DataChannelFormat.JSONL,
        dataChannelMedium = DataChannelMedium.STDIO,
    )
