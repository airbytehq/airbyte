/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField

data object OracleSourceCdcScn : MetaField {
    override val id: String = MetaField.META_PREFIX + "cdc_scn"
    override val type: FieldType = CdcIntegerMetaFieldType
}
