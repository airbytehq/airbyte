/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.jdbc.ColumnMetadata

/** Maps a [ColumnMetadata] to a [FieldType] in a many-to-one relationship. */
fun interface ColumnMetadataToFieldTypeMapper {

    fun toFieldType(c: ColumnMetadata): FieldType

}
