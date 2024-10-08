/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.Serializable

interface AirbyteRecordMapper<T> : (AirbyteValue) -> T, Serializable

@Singleton
@Secondary
class AirbyteRecordIdentityMapper : AirbyteRecordMapper<AirbyteValue> {
    override fun invoke(input: AirbyteValue): AirbyteValue = input
}
