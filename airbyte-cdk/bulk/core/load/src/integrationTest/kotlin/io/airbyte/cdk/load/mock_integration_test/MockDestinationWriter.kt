/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.test.mock.MockDestinationBackend
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.airbyte.cdk.load.test.mock.MockDestinationConfiguration
import io.airbyte.cdk.load.test.mock.MockDestinationDataDumper.getFilename
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(env = [MOCK_TEST_MICRONAUT_ENVIRONMENT])
class MockDestinationWriter(
    private val config: MockDestinationConfiguration,
) : DestinationWriter {
    override suspend fun setup() {
        if (config.foo != 0) {
            throw IllegalArgumentException("Foo should be 0")
        }
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return MockStreamLoader(stream)
    }
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class MockStreamLoader(override val stream: DestinationStream) : StreamLoader {
    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            when (val importType = stream.importType) {
                is Append -> {
                    MockDestinationBackend.commitFrom(
                        getFilename(stream.descriptor, staging = true),
                        getFilename(stream.descriptor)
                    )
                }
                is Dedupe -> {
                    MockDestinationBackend.commitAndDedupeFrom(
                        getFilename(stream.descriptor, staging = true),
                        getFilename(stream.descriptor),
                        importType.primaryKey,
                        importType.cursor,
                    )
                }
                else -> throw IllegalArgumentException("Unsupported import type $importType")
            }
            MockDestinationBackend.deleteOldRecords(
                getFilename(stream.descriptor),
                stream.minimumGenerationId
            )
        } else {
            logger.info {
                "Skipping commit because stream ${stream.descriptor.toPrettyString()} was not successful"
            }
        }
    }
}
