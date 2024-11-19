/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg_v2

import io.airbyte.cdk.load.check.DestinationChecker
import javax.inject.Singleton

@Singleton
class IcebergV2Checker : DestinationChecker<IcebergV2Configuration> {
    override fun check(config: IcebergV2Configuration) {
        // TODO validate the config
    }
}
