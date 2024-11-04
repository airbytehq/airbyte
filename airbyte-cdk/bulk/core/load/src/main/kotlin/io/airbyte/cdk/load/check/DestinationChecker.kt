/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.NullType

/**
 * A check operation that is run before the destination is used.
 *
 * * Implementors must provide a [check] method that validates the configuration.
 * * Implementors may provide a [cleanup] method that is run after the check is complete.
 * * [check] should throw an exception if the configuration is invalid.
 * * [cleanup] should not throw exceptions.
 * * Implementors should not perform any side effects in the constructor.
 * * Implementors should not throw exceptions in the constructor.
 * * Implementors should not inject configuration; only use the config passed in [check].
 */
interface DestinationChecker<C : DestinationConfiguration> {
    fun mockStream() =
        DestinationStream(
            descriptor = DestinationStream.Descriptor("testing", "test"),
            importType = Append,
            schema = NullType,
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 1,
        )

    fun check(config: C)
    fun cleanup() {}
}
