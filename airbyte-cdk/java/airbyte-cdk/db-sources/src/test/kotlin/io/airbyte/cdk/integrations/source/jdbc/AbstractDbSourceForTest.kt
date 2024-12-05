/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.AbstractDatabase
import io.airbyte.cdk.integrations.source.relationaldb.AbstractDbSource
import io.airbyte.protocol.models.v0.AirbyteStateMessage

abstract class AbstractDbSourceForTest<DataType, Database : AbstractDatabase?>(
    driverClassName: String
) : AbstractDbSource<DataType, Database>(driverClassName) {
    public override fun getSupportedStateType(
        config: JsonNode?
    ): AirbyteStateMessage.AirbyteStateType {
        return super.getSupportedStateType(config)
    }
}
