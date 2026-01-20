/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

/** This is used only in tests. */
class ConnectorUncleanExitException(val exitCode: Int) :
    Exception("Connector process exited uncleanly: $exitCode")
