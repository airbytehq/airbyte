/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.general

import io.airbyte.configoss.ConnectorJobOutput
import io.airbyte.configoss.StandardCheckConnectionInput
import io.airbyte.workers.TestHarness

interface CheckConnectionTestHarness :
    TestHarness<StandardCheckConnectionInput, ConnectorJobOutput>
