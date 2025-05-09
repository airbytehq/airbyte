/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.check.DestinationCheckerSync
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.pipeline.ByPrimaryKeyInputPartitioner
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.airbyte.cdk.load.test.mock.MockDestinationConfiguration
import io.airbyte.cdk.load.write.WriteOperation
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.InputStream

@Factory
@Requires(env = [MOCK_TEST_MICRONAUT_ENVIRONMENT])
class MockDestinationBeansFactory {
    @Singleton
    fun getChecker(
        catalog: DestinationCatalog,
        @Named("inputStream") stdinPipe: InputStream,
        taskLauncher: DestinationTaskLauncher,
        syncManager: SyncManager,
    ) =
        DestinationCheckerSync<MockDestinationConfiguration>(
            catalog,
            stdinPipe,
            WriteOperation(taskLauncher, syncManager),
        ) { _, _ ->
            // do nothing, we don't need to actually clean anything up
        }

    @Singleton fun getPartitioner() = ByPrimaryKeyInputPartitioner()
}
