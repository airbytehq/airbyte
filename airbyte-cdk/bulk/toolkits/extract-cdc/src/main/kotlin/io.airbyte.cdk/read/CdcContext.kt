/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.output.OutputConsumer
import jakarta.inject.Singleton

@Singleton
data class CdcContext(
    val outputConsumer: OutputConsumer,
    val debeziumManager: DebeziumManager,
    val positionMapperFactory: CdcPositionMapper.Factory,
    val eventConverter: DebeziumEventConverter,
    val initialCdcStateCreatorFactory: InitialCdcStateCreatorFactory,
    val cdcGlobalLockResource: CdcGlobalLockResource,
)
