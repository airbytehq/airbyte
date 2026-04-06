/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2

import io.airbyte.cdk.AirbyteDestinationRunner

/**
 * Main entry point for the Redshift v2 destination connector.
 * 
 * This connector uses the Bulk CDK with Direct Load pattern.
 */
fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}
