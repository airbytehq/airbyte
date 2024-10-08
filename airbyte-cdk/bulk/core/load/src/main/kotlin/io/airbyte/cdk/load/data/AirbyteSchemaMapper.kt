/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface AirbyteSchemaMapper<T> : (AirbyteType) -> T

@Singleton
@Secondary
class AirbyteSchemaIdentityMapper : AirbyteSchemaMapper<AirbyteType> {
    override fun invoke(input: AirbyteType): AirbyteType = input
}
