/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

interface CheckConnectionTestHarness :
    TestHarness<StandardCheckConnectionInput, ConnectorJobOutput>
