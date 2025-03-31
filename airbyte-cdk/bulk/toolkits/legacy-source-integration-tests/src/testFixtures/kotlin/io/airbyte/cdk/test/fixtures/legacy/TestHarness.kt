/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import java.nio.file.Path

interface TestHarness<InputType, OutputType> {
    /**
     * Blocking call to run the worker's workflow. Once this is complete, getStatus should return
     * either COMPLETE, FAILED, or CANCELLED.
     */
    fun run(inputType: InputType, jobRoot: Path): OutputType

    /**
     * Cancels in-progress workers. Although all workers support cancel, in reality only the
     * asynchronous [DefaultReplicationWorker]'s cancel is used.
     */
    fun cancel()
}
