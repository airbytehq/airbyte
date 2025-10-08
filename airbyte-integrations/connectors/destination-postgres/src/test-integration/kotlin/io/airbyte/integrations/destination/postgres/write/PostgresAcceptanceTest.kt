/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import org.junit.jupiter.api.Disabled

object PostgresDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> = emptyList()

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> = emptyMap()
}

object PostgresDataCleaner : DestinationCleaner {
    override fun cleanup() {}
}

class PostgresSpecification : ConfigurationSpecification()

class PostgresAcceptanceTest : BasicFunctionalityIntegrationTest(
    configContents = "{}",
    configSpecClass = PostgresSpecification::class.java,
    dataDumper = PostgresDataDumper,
    destinationCleaner = PostgresDataCleaner,
    isStreamSchemaRetroactive = true,
    dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
    stringifySchemalessObjects = true,
    schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
    schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
    unionBehavior = UnionBehavior.PASS_THROUGH,
    supportFileTransfer = false,
    commitDataIncrementally = false,
    commitDataIncrementallyOnAppend = false,
    commitDataIncrementallyToEmptyDestinationOnAppend = true,
    commitDataIncrementallyToEmptyDestinationOnDedupe = false,
    allTypesBehavior = StronglyTyped(
        integerCanBeLarge = true,
        numberCanBeLarge = true,
        nestedFloatLosesPrecision = false,
    ),
    unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    nullEqualsUnset = true,
)
