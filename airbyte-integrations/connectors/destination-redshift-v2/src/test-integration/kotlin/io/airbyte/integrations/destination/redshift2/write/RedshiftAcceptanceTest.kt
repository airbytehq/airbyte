/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write

import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfigurationFactory
import io.airbyte.integrations.destination.redshift2.config.RedshiftSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll

/**
 * Full end-to-end acceptance test for the Redshift destination in S3 staging mode.
 *
 * Runs the connector as a process via the CDK test harness and verifies typed final-table output.
 * Config is read from the `secrets/config_staging.json` secrets file, which must contain valid
 * Redshift cluster + S3 staging credentials.
 *
 * This test exercises ~25 inherited test methods from [BasicFunctionalityIntegrationTest] covering:
 * - Core writes (single record, no data, no columns, clear)
 * - Append mode (multi-sync, many-stream concurrency)
 * - Dedup/CDC (integer/string PKs, cursor changes, PK changes, hard-delete semantics)
 * - Truncate refresh (success, failure recovery, interrupted truncate)
 * - Schema evolution (column add/drop/type-change in append and overwrite modes)
 * - Data types (all basic types, container types, unions, unknown types)
 * - Edge cases (funky characters, multiple namespaces, SQL reserved words)
 * - Numeric precision (numeric(38,9) truncation/rounding)
 */
class RedshiftAcceptanceTest :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Path.of(CONFIG_PATH)),
        configSpecClass = RedshiftSpecification::class.java,
        dataDumper =
            RedshiftDataDumper { spec ->
                RedshiftConfigurationFactory()
                    .makeWithoutExceptionHandling(spec as RedshiftSpecification)
            },
        destinationCleaner = RedshiftDataCleaner,
        recordMangler = RedshiftExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
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
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
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
