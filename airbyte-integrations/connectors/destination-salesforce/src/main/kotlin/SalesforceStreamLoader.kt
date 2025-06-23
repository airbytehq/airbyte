/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamLoader

class SalesforceStreamLoader(override val stream: DestinationStream) : StreamLoader {}
