/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3

import io.airbyte.cdk.core.IntegrationCommand
import io.airbyte.cdk.core.context.AirbyteConnectorRunner

fun main(args: Array<String>) {
    AirbyteConnectorRunner.run(IntegrationCommand::class.java, *args)
}
