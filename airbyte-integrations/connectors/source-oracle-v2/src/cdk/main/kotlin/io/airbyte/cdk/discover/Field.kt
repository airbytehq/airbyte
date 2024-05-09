/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

/** Union type for fields in an Airbyte record. */
sealed interface FieldOrMetaField {
    val id: String
    val type: FieldType
}

data class Field(override val id: String, override val type: FieldType) : FieldOrMetaField

sealed interface MetaField : FieldOrMetaField

data object AirbyteCdcLsnMetaField : MetaField {

    override val id: String
        get() = "_ab_cdc_lsn"

    override val type: FieldType
        get() = StringFieldType
}

data object AirbyteCdcUpdatedAtMetaField : MetaField {

    override val id: String
        get() = "_ab_cdc_updated_at"

    override val type: FieldType
        get() = OffsetDateTimeFieldType
}


data object AirbyteCdcDeletedAtMetaField : MetaField {

    override val id: String
        get() = "_ab_cdc_deleted_at"

    override val type: FieldType
        get() = OffsetDateTimeFieldType
}
