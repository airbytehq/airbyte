/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import org.junit.jupiter.api.Test

abstract class BigqueryWriteTest(configContents: String) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        BigquerySpecification::class.java,
        dataDumper = FakeDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        // this is almost all wrong probably
        NoopExpectedRecordMapper,
        verifyDataWriting = false,
        isStreamSchemaRetroactive = false,
        supportsDedup = false,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        preserveUndeclaredFields = false,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior = Untyped,
    )

class BigqueryGcsWriteTest : BigqueryWriteTest("""{"option": "purple"}""") {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class BigqueryDirectLoadWriteTest : BigqueryWriteTest("""{"option": "fish"}""")
