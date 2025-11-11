/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

/**
 * Thrown when the destination completes successfully, but some streams were indicated as incomplete
 * by upstream. Without throwing an exception the sync will not be marked as succeed by the
 * platform.
 *
 * TODO: Once the API with platform is updated to not require an exceptional exit code, remove this.
 */
class StreamsIncompleteException : Exception() {
    override val message = "Some streams were indicated as incomplete by upstream."
}
