/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.mock_integration_test

import io.airbyte.cdk.test.util.NoopDestinationCleaner
import io.airbyte.cdk.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.test.util.NoopNameMapper
import io.airbyte.cdk.test.write.BasicFunctionalityIntegrationTest

class MockBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        MockDestinationSpecification(),
        MockDestinationDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        NoopNameMapper
    )
