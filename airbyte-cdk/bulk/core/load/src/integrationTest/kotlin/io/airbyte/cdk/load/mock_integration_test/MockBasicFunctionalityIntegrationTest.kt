/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper

class MockBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        MockDestinationSpecification(),
        MockDestinationDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        NoopNameMapper
    )
