/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.postgres.PostgresConfigUpdater
import io.airbyte.integrations.destination.postgres.PostgresContainerHelper
import io.airbyte.integrations.destination.postgres.spec.PostgresConfigurationFactory
import io.airbyte.integrations.destination.postgres.spec.PostgresSpecification
import io.airbyte.integrations.destination.postgres.spec.PostgresSpecificationCloud
import org.junit.jupiter.api.BeforeAll

class PostgresAcceptanceTest :
    BasicFunctionalityIntegrationTest(
        configContents =
            """{
                        "host": "replace_me_host",
                        "port": replace_me_port,
                        "database": "replace_me_database",
                        "schema": "public",
                        "username": "replace_me_username",
                        "password": "replace_me_password"
                    }""",
        configSpecClass = PostgresSpecificationCloud::class.java,
        dataDumper =
            PostgresDataDumper { spec ->
                val configOverrides = buildConfigOverridesForTestContainer()
                PostgresConfigurationFactory()
                    .makeWithOverrides(spec as PostgresSpecification, configOverrides)
            },
        destinationCleaner = PostgresDataCleaner,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        stringifyUnionObjects = false,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = true,
                nestedFloatLosesPrecision = true,
            ),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        configUpdater = PostgresConfigUpdater(),
        recordMangler = PostgresTimestampNormalizationMapper,
        useDataFlowPipeline = true,
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            PostgresContainerHelper.start()
        }
    }
}
