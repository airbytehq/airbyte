/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.probably_core_stuff

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType

object LegacyTypingDedupingUtil {
    // See old CDK's Union#chooseType
    fun chooseType(union: UnionType): AirbyteType {
        return union.options.minBy {
            when (it) {
                ArrayTypeWithoutSchema,
                is ArrayType -> -2
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> -1

                // TODO use same order as AirbyteProtocolType
                BooleanType -> TODO()
                DateType -> TODO()
                IntegerType -> TODO()
                NumberType -> TODO()
                StringType -> TODO()
                TimeTypeWithTimezone -> TODO()
                TimeTypeWithoutTimezone -> TODO()
                TimestampTypeWithTimezone -> TODO()
                TimestampTypeWithoutTimezone -> TODO()
                is UnknownType -> TODO()
                is UnionType -> Int.MAX_VALUE
            }
        }
    }
}
