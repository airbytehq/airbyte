/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField

/** MongoDB CDC meta fields added to every stream. */
enum class MongoDbCdcMetaFields(
    override val type: FieldType,
) : MetaField {
    CDC_CURSOR(CdcIntegerMetaFieldType),
    ;

    override val id: String
        get() = MetaField.META_PREFIX + name.lowercase()
}
