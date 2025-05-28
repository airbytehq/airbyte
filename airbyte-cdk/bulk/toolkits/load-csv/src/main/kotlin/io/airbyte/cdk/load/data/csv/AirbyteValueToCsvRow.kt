/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue

fun ObjectValue.toCsvRecord(schema: ObjectType, processor: CsvValueProcessor): List<Any> {
    return schema.properties.map { (key, _) -> processor.process(values[key]) }
}
