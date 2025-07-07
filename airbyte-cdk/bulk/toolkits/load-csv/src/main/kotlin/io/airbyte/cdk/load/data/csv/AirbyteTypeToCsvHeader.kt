/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.ObjectType

class AirbyteTypeToCsvHeader {
    fun convert(schema: ObjectType): Array<String> {
        return schema.properties.map { it.key }.toTypedArray()
    }
}

fun ObjectType.toCsvHeader(): Array<String> {
    return AirbyteTypeToCsvHeader().convert(this)
}
