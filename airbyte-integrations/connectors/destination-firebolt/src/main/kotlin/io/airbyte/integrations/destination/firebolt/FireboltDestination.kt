/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt

import io.airbyte.cdk.AirbyteDestinationRunner

/** Main entry point for the Firebolt V2 destination connector. */
fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}
