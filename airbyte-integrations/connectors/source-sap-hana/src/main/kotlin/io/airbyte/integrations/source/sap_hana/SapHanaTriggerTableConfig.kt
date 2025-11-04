/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.TriggerTableConfig
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import jakarta.inject.Singleton

@Singleton
class SapHanaTriggerTableConfig(sapHanaSourceConfiguration: SapHanaSourceConfiguration) :
    TriggerTableConfig() {

    override val cursorFieldType: FieldType = OffsetDateTimeFieldType
    override val cdcEnabled: Boolean = sapHanaSourceConfiguration.isCdc()
}
