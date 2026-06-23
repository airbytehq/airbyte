/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift

import io.airbyte.cdk.AirbyteDestinationRunner

/** Main entry point for the Redshift v2 destination connector. */
fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}
