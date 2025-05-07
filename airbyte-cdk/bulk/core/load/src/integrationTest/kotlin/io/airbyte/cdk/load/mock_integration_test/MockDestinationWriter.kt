/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import javax.inject.Singleton

@Singleton
class MockDestinationWriter : DestinationWriter {
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
        }
    }

    companion object {
        fun getFilename(stream: DestinationStream.Descriptor, staging: Boolean = false) =
            getFilename(stream.namespace, stream.name, staging)
        fun getFilename(namespace: String?, name: String, staging: Boolean = false) =
            if (staging) {
                "(${namespace},${name},staging)"
            } else {
                "(${namespace},${name})"
            }
    }
}
