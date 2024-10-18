/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

class ConnectorUncleanExitException(val exitCode: Int) :
    Exception("Destination process exited uncleanly: $exitCode")
