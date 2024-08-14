/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test

import io.airbyte.cdk.AirbyteDestinationRunner
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.io.FileInputStream
import java.io.InputStream

class E2EDestination {
    companion object {
        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteDestinationRunner.run(*args)
        }
    }
}

@Factory
class InputStreamFactory {
    @Singleton
    @Primary
    fun make(): InputStream {
        return FileInputStream("test.jsonl")
    }
}
