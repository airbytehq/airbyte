/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy


interface CheckConnectionTestHarness :
    TestHarness<StandardCheckConnectionInput, ConnectorJobOutput>
