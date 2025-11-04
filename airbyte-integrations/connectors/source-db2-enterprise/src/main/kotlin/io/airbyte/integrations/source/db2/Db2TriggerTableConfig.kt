/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2

import io.airbyte.cdk.TriggerTableConfig
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.integrations.source.db2.config.Db2SourceConfiguration
import jakarta.inject.Singleton

@Singleton
class Db2TriggerTableConfig(db2SourceConfiguration: Db2SourceConfiguration) : TriggerTableConfig() {

    override val cursorFieldType: FieldType = LocalDateTimeFieldType
    override val cdcEnabled: Boolean = db2SourceConfiguration.isCdc()
}
