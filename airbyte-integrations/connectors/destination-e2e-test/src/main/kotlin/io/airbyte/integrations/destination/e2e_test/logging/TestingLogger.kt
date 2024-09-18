/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.e2e_test.logging

import io.airbyte.protocol.models.v0.AirbyteRecordMessage

interface TestingLogger {
    enum class LoggingType {
        FirstN,
        EveryNth,
        RandomSampling
    }

    fun log(recordMessage: AirbyteRecordMessage?)
}
