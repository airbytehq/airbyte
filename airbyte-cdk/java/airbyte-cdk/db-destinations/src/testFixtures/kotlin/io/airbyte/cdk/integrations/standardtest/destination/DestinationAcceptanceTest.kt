/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import io.airbyte.cdk.integrations.standardtest.destination.*
import io.airbyte.cdk.integrations.standardtest.destination.comparator.BasicTestDataComparator
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.workers.helper.ConnectorConfigUpdater
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import org.junit.jupiter.api.*
import org.mockito.Mockito

private val LOGGER = KotlinLogging.logger {}

abstract class DestinationAcceptanceTest(
    // If false, ignore counts and only verify the final state message.
    verifyIndividualStateAndCounts: Boolean = false,
    override val useV2Fields: Boolean = false,
    override val supportsChangeCapture: Boolean = false,
    override val expectNumericTimestamps: Boolean = false,
    override val expectSchemalessObjectsCoercedToStrings: Boolean = false,
    override val expectUnionsPromotedToDisjointRecords: Boolean = false
): BaseRecordDestinationAcceptanceTest, AbstractDestinationAcceptanceTest(
    verifyIndividualStateAndCounts=verifyIndividualStateAndCounts
) {
    override var testSchemas: HashSet<String> = HashSet()

    override var _testDataComparator: TestDataComparator = getTestDataComparator()

    override val mConnectorConfigUpdater: ConnectorConfigUpdater = Mockito.mock(ConnectorConfigUpdater::class.java)
}
