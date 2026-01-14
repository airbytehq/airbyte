/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.integrationTest.DLQ_INTEGRATION_TEST_ENV
import io.airbyte.cdk.load.spec.SpecTest

class DlqSpecTest : SpecTest(additionalMicronautEnvs = listOf(DLQ_INTEGRATION_TEST_ENV)) {}
